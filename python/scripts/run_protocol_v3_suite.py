"""Run the protocol V3 vector-geometry checks on the normalized HF transport data.

Protocol V3 is exploratory but constrained:
- no global fit,
- no score-below-threshold as the main criterion,
- priority on stability, invariance, and relative structure.

The implementation below keeps the science honest by using only observed or
fixed reference quantities from the manifest and the published HF tables.
It builds a dimensionless vector space, then checks whether the geometry is
stable across materials, leave-one-material-out folds, and frequency bands.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import time
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


REQUIRED_MATERIALS = ("cu", "al", "ag", "fe")
OPTIONAL_MATERIALS = ("au", "ni")
FREQ_BANDS = (
    ("bf_proxy", 0.0, 1.0e3),
    ("hf_classic", 1.0e3, 1.0e5),
    ("hf_advanced_proxy", 1.0e5, float("inf")),
)
CONDUCTIVITY_REFERENCE = 1.0 / 1.724e-8


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_manifest(root: Path) -> dict:
    manifest_path = root / "python" / "data" / "hf_transport_manifest.json"
    return load_json(manifest_path)


def dataset_path(root: Path, entry: dict) -> Path:
    relative_path = entry.get("file") or entry.get("path")
    if not relative_path:
        raise ValueError("Dataset entry is missing a file path")
    return root / relative_path.replace("/", "\\")


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def pstdev(values: list[float]) -> float:
    return statistics.pstdev(values) if len(values) > 1 else 0.0


def coefficient_of_variation(values: list[float]) -> float:
    average = mean(values)
    return pstdev(values) / max(abs(average), 1.0e-24)


def euclidean_distance(left: np.ndarray, right: np.ndarray) -> float:
    return float(np.linalg.norm(left - right))


def pairwise_distances(vectors: list[np.ndarray]) -> list[float]:
    distances: list[float] = []
    for index, left in enumerate(vectors):
        for right in vectors[index + 1 :]:
            distances.append(euclidean_distance(left, right))
    return distances


def pca_fit(vectors: list[np.ndarray]) -> dict:
    matrix = np.vstack(vectors)
    center = matrix.mean(axis=0)
    centered = matrix - center
    covariance = np.cov(centered, rowvar=False, ddof=1)
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    order = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[order]
    eigenvectors = eigenvectors[:, order]
    total = float(eigenvalues.sum()) if float(eigenvalues.sum()) else 1.0
    explained = [float(value / total) for value in eigenvalues]
    scores = centered @ eigenvectors
    return {
        "center": center,
        "eigenvalues": eigenvalues,
        "eigenvectors": eigenvectors,
        "explained_variance_ratio": explained,
        "scores": scores,
    }


def pca_transform(model: dict, vectors: list[np.ndarray]) -> np.ndarray:
    matrix = np.vstack(vectors)
    centered = matrix - model["center"]
    return centered @ model["eigenvectors"]


def band_for_frequency(frequency_hz: float) -> str:
    for label, lower, upper in FREQ_BANDS:
        if lower < frequency_hz <= upper or (lower == 0.0 and frequency_hz <= upper):
            return label
    return "unknown"


def nearest_neighbor(name: str, centroids: dict[str, np.ndarray]) -> tuple[str, float]:
    origin = centroids[name]
    best_name = ""
    best_distance = float("inf")
    for other_name, other_vector in centroids.items():
        if other_name == name:
            continue
        distance = euclidean_distance(origin, other_vector)
        if distance < best_distance:
            best_name = other_name
            best_distance = distance
    return best_name, best_distance


def rank_signature(name: str, centroids: dict[str, np.ndarray]) -> list[str]:
    origin = centroids[name]
    ordered = sorted(
        ((other_name, euclidean_distance(origin, other_vector)) for other_name, other_vector in centroids.items() if other_name != name),
        key=lambda item: item[1],
    )
    return [other_name for other_name, _ in ordered]


def load_material_series(root: Path) -> list[dict]:
    manifest = load_manifest(root)
    datasets = manifest.get("datasets", {})
    materials: list[dict] = []

    for label, entry in datasets.items():
        path = dataset_path(root, entry)
        dataset = load_json(path)
        method = dataset.get("method", {})
        assumptions = method.get("assumptions", {})
        rho = float(assumptions.get("rho_ohm_m"))
        mu_r = float(assumptions.get("mu_r_eff", 1.0))
        records = dataset.get("records", [])
        if not records:
            raise ValueError(f"Dataset {label} has no records")

        frequencies = [float(record["frequency_hz"]) for record in records]
        depths = [float(record["skin_depth_m"]) for record in records]
        delta_ref = depths[0]
        frequency_ref = min(frequencies)
        amplitude_ref = delta_ref * math.sqrt(frequency_ref)
        sigma = 1.0 / rho

        points = []
        for record in records:
            frequency_hz = float(record["frequency_hz"])
            skin_depth_m = float(record["skin_depth_m"])
            amplitude_ratio = (skin_depth_m * math.sqrt(frequency_hz)) / amplitude_ref
            magnetic_flag = 1.0 if mu_r > 1.5 else 0.0
            band = band_for_frequency(frequency_hz)
            point = {
                "material": label,
                "frequency_hz": frequency_hz,
                "skin_depth_m": skin_depth_m,
                "magnetic_flag": magnetic_flag,
                "sigma_proxy": sigma,
                "band": band,
                "amplitude_ratio": amplitude_ratio,
                "raw_vector": np.array([frequency_hz, skin_depth_m, magnetic_flag, sigma], dtype=float),
                "vector": np.array(
                    [
                        math.log10(amplitude_ratio),
                        sigma / CONDUCTIVITY_REFERENCE,
                    ],
                    dtype=float,
                ),
            }
            points.append(point)

        materials.append(
            {
                "label": label,
                "path": str(path.relative_to(root)),
                "rho_ohm_m": rho,
                "mu_r_eff": mu_r,
                "conductivity_proxy": sigma,
                "delta_ref": delta_ref,
                "frequency_ref": frequency_ref,
                "amplitude_ref": amplitude_ref,
                "records": records,
                "points": points,
            }
        )

    return materials


def summarize_materials(materials: list[dict]) -> list[dict]:
    summary: list[dict] = []
    for material in materials:
        vectors = [point["vector"] for point in material["points"]]
        raw_vectors = [point["raw_vector"] for point in material["points"]]
        centroid = np.mean(np.vstack(vectors), axis=0)
        raw_centroid = np.mean(np.vstack(raw_vectors), axis=0)
        spread = [euclidean_distance(vector, centroid) for vector in vectors]
        raw_spread = [euclidean_distance(vector, raw_centroid) for vector in raw_vectors]
        summary.append(
            {
                "label": material["label"],
                "path": material["path"],
                "rho_ohm_m": material["rho_ohm_m"],
                "mu_r_eff": material["mu_r_eff"],
                "conductivity_proxy": material["conductivity_proxy"],
                "delta_ref": material["delta_ref"],
                "frequency_ref": material["frequency_ref"],
                "amplitude_ref": material["amplitude_ref"],
                "vector_centroid": centroid.tolist(),
                "raw_centroid": raw_centroid.tolist(),
                "vector_radius": mean([float(value) for value in spread]),
                "raw_radius": mean([float(value) for value in raw_spread]),
                "point_count": len(vectors),
            }
        )
    return summary


def material_centroids(materials: list[dict], field: str = "vector") -> dict[str, np.ndarray]:
    centroids: dict[str, np.ndarray] = {}
    for material in materials:
        vectors = [point[field] for point in material["points"]]
        centroids[material["label"]] = np.mean(np.vstack(vectors), axis=0)
    return centroids


def material_point_cloud(materials: list[dict], field: str = "vector") -> list[np.ndarray]:
    vectors: list[np.ndarray] = []
    for material in materials:
        vectors.extend(point[field] for point in material["points"])
    return vectors


def full_geometry_test(materials: list[dict]) -> dict:
    centroids = material_centroids(materials, "vector")
    raw_centroids = material_centroids(materials, "raw_vector")
    within_radii = []
    raw_within_radii = []

    for material in materials:
        centroid = centroids[material["label"]]
        raw_centroid = raw_centroids[material["label"]]
        within = [euclidean_distance(point["vector"], centroid) for point in material["points"]]
        raw_within = [euclidean_distance(point["raw_vector"], raw_centroid) for point in material["points"]]
        within_radii.append(mean(within))
        raw_within_radii.append(mean(raw_within))

    between = pairwise_distances(list(centroids.values()))
    raw_between = pairwise_distances(list(raw_centroids.values()))
    pca_model = pca_fit(material_point_cloud(materials, "vector"))
    explained = pca_model["explained_variance_ratio"]
    top2_explained = sum(explained[:2]) if len(explained) >= 2 else sum(explained)

    separation_ratio = min(between) / max(within_radii) if within_radii and max(within_radii) else float("inf")
    raw_separation_ratio = min(raw_between) / max(raw_within_radii) if raw_within_radii and max(raw_within_radii) else float("inf")
    nearest_neighbors = {name: nearest_neighbor(name, centroids)[0] for name in centroids}

    supported = separation_ratio > 1.5 and top2_explained > 0.8
    return {
        "centroids": {name: vector.tolist() for name, vector in centroids.items()},
        "raw_centroids": {name: vector.tolist() for name, vector in raw_centroids.items()},
        "within_radius_mean": mean(within_radii),
        "raw_within_radius_mean": mean(raw_within_radii),
        "between_distance_mean": mean(between),
        "raw_between_distance_mean": mean(raw_between),
        "separation_ratio": separation_ratio,
        "raw_separation_ratio": raw_separation_ratio,
        "pca_explained_variance_ratio": [float(value) for value in explained],
        "pca_top2_explained": top2_explained,
        "nearest_neighbors": nearest_neighbors,
        "verdict": "supported" if supported else "contradicted",
        "reason": (
            "The invariant-based 2D space separates material centroids more clearly than the raw space and the leading PCA plane captures most of the variance."
            if supported
            else "The proposed invariant-based vector space does not yet stabilize the material geometry enough."
        ),
    }


def leave_one_material_out(materials: list[dict]) -> dict:
    folds = []
    for held_out in materials:
        train_materials = [material for material in materials if material["label"] != held_out["label"]]
        train_centroids = material_centroids(train_materials, "vector")
        train_vectors = material_point_cloud(train_materials, "vector")
        train_pca = pca_fit(train_vectors)

        held_centroid = material_centroids([held_out], "vector")[held_out["label"]]
        projected_train = pca_transform(train_pca, list(train_centroids.values()))
        projected_held = pca_transform(train_pca, [held_centroid])[0]

        projected_centroids = {
            name: vector for name, vector in zip(train_centroids.keys(), projected_train)
        }

        full_rank = rank_signature(held_out["label"], material_centroids(materials, "vector"))
        projected_rank = sorted(
            ((name, euclidean_distance(projected_held, vector)) for name, vector in projected_centroids.items()),
            key=lambda item: item[1],
        )
        projected_order = [name for name, _ in projected_rank]
        projected_nn = projected_order[0]
        full_nn = full_rank[0] if full_rank else ""

        displacement = euclidean_distance(held_centroid, np.mean(np.vstack(train_vectors), axis=0))
        order_match = full_nn == projected_nn
        folds.append(
            {
                "held_out": held_out["label"],
                "train_family": [material["label"] for material in train_materials],
                "full_nearest_neighbor": full_nn,
                "projected_nearest_neighbor": projected_nn,
                "full_rank": full_rank,
                "projected_rank": projected_order,
                "displacement_to_train_center": displacement,
                "order_match": order_match,
                "pca_top2_explained": sum(train_pca["explained_variance_ratio"][:2]),
            }
        )

    supported = all(fold["order_match"] for fold in folds)
    return {
        "folds": folds,
        "verdict": "supported" if supported else "contradicted",
        "reason": (
            "The held-out material always falls back into the same nearest-neighbor geometry under leave-one-material-out."
            if supported
            else "At least one held-out material changes its nearest-neighbor geometry when the basis is rebuilt."
        ),
    }


def regime_continuity(materials: list[dict]) -> dict:
    bands: dict[str, list[dict]] = defaultdict(list)
    for material in materials:
        for point in material["points"]:
            bands[point["band"]].append(point)

    band_centroids: dict[str, dict[str, np.ndarray]] = {}
    band_pca_top2: dict[str, float] = {}
    band_nn: dict[str, dict[str, str]] = {}
    band_shifts: dict[str, dict[str, float]] = {}

    full_centroids = material_centroids(materials, "vector")
    for band_name, points in bands.items():
        material_groups: dict[str, list[np.ndarray]] = defaultdict(list)
        for point in points:
            material_groups[point["material"]].append(point["vector"])
        centroids = {name: np.mean(np.vstack(vectors), axis=0) for name, vectors in material_groups.items()}
        band_centroids[band_name] = {name: vector.tolist() for name, vector in centroids.items()}
        if len(points) > 1:
            band_pca_top2[band_name] = sum(pca_fit([point["vector"] for point in points])["explained_variance_ratio"][:2])
        else:
            band_pca_top2[band_name] = 0.0
        band_nn[band_name] = {name: nearest_neighbor(name, centroids)[0] for name in centroids} if len(centroids) > 1 else {}
        band_shifts[band_name] = {
            name: euclidean_distance(vector, full_centroids[name])
            for name, vector in centroids.items()
        }

    reference_band = "bf_proxy" if "bf_proxy" in band_centroids else next(iter(band_centroids), "")
    reference_nn = band_nn.get(reference_band, {})
    nn_stable = True
    drift_values = []
    for band_name, neighbors in band_nn.items():
        for material_name, neighbor_name in neighbors.items():
            if material_name in reference_nn and reference_nn[material_name] != neighbor_name:
                nn_stable = False
            drift_values.append(band_shifts[band_name][material_name])

    coverage = {label: label in band_centroids for label, _, _ in FREQ_BANDS}
    explicit_dc_available = False
    supported = nn_stable and all(value > 0.75 for value in band_pca_top2.values() if value)
    return {
        "coverage": coverage,
        "explicit_dc_available": explicit_dc_available,
        "band_centroids": band_centroids,
        "band_pca_top2": band_pca_top2,
        "band_nearest_neighbors": band_nn,
        "band_mean_shift": mean(drift_values) if drift_values else 0.0,
        "band_max_shift": max(drift_values) if drift_values else 0.0,
        "verdict": "supported" if supported else "partiel",
        "reason": (
            "The relative material geometry stays stable across the observed low/mid/high frequency bands."
            if supported
            else "The band geometry remains readable, but one or more bands do not preserve the same nearest-neighbor structure."
        ),
    }


def stability_statistics(materials: list[dict]) -> dict:
    raw_centroids = material_centroids(materials, "raw_vector")
    vector_centroids = material_centroids(materials, "vector")
    raw_pairwise = pairwise_distances(list(raw_centroids.values()))
    vector_pairwise = pairwise_distances(list(vector_centroids.values()))

    raw_cv = coefficient_of_variation(raw_pairwise)
    vector_cv = coefficient_of_variation(vector_pairwise)

    leave_one_out = []
    for held_out in materials:
        train_materials = [material for material in materials if material["label"] != held_out["label"]]
        train_centroids = material_centroids(train_materials, "vector")
        train_pairwise = pairwise_distances(list(train_centroids.values()))
        leave_one_out.append(coefficient_of_variation(train_pairwise))

    supported = vector_cv < raw_cv and max(leave_one_out) <= raw_cv * 1.15
    return {
        "raw_pairwise_cv": raw_cv,
        "vector_pairwise_cv": vector_cv,
        "leave_one_out_pairwise_cv": leave_one_out,
        "improvement_ratio": vector_cv / max(raw_cv, 1.0e-24),
        "verdict": "supported" if supported else "contradicted",
        "reason": (
            "The invariant-based vector space lowers the cross-material spread and the result survives leave-one-out recomputation."
            if supported
            else "The invariant-based vector space does not reduce the spread enough to count as stable."
        ),
    }


def scalar_reduction(materials: list[dict], vector_model: dict) -> dict:
    points = material_point_cloud(materials, "vector")
    scores = vector_model["scores"][:, 0]
    if len(scores) != len(points):
        raise ValueError("PCA score count mismatch")

    offset = 0
    material_scalars: dict[str, float] = {}
    for material in materials:
        count = len(material["points"])
        material_scalars[material["label"]] = float(np.mean(scores[offset : offset + count]))
        offset += count

    scalar_pairwise = pairwise_distances([np.array([value], dtype=float) for value in material_scalars.values()])
    scalar_cv = coefficient_of_variation(scalar_pairwise)
    vector_centroids = material_centroids(materials, "vector")
    vector_pairwise = pairwise_distances(list(vector_centroids.values()))
    vector_cv = coefficient_of_variation(vector_pairwise)
    supported = scalar_cv <= vector_cv * 1.05
    return {
        "material_scalar_centroids": material_scalars,
        "scalar_pairwise_distances": scalar_pairwise,
        "scalar_pairwise_cv": scalar_cv,
        "vector_pairwise_cv": vector_cv,
        "verdict": "supported" if supported else "contradicted",
        "reason": (
            "The first principal component preserves the cross-material stability of the invariant vector geometry."
            if supported
            else "The scalar collapse is not as stable as the vector form, so the vector representation should be kept."
        ),
    }


def make_plots(materials: list[dict], geometry: dict, stability: dict, result_dir: Path) -> dict:
    plots_dir = result_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    vector_points = material_point_cloud(materials, "vector")
    vector_labels = [material["label"] for material in materials for _ in material["points"]]
    band_labels = [point["band"] for material in materials for point in material["points"]]
    pca_model = pca_fit(vector_points)
    scores = pca_model["scores"]

    fig, ax = plt.subplots(figsize=(9, 7), constrained_layout=True)
    material_order = [material["label"] for material in materials]
    color_map = {label: plt.cm.tab10(index) for index, label in enumerate(material_order)}
    marker_map = {"bf_proxy": "o", "hf_classic": "s", "hf_advanced_proxy": "^"}

    for index, (score, material_label, band_label) in enumerate(zip(scores, vector_labels, band_labels)):
        ax.scatter(
            score[0],
            score[1],
            s=58,
            color=color_map.get(material_label, "black"),
            marker=marker_map.get(band_label, "o"),
            alpha=0.9,
            edgecolor="white",
            linewidth=0.5,
        )
        if index % 5 == 0:
            ax.text(score[0] + 0.02, score[1] + 0.02, material_label.upper(), fontsize=8)

    ax.set_title("Protocol V3 - PCA projection of the vector space")
    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    ax.axhline(0.0, color="#999999", linewidth=0.8)
    ax.axvline(0.0, color="#999999", linewidth=0.8)

    legend_handles = []
    for label in material_order:
        legend_handles.append(ax.scatter([], [], color=color_map[label], label=label.upper(), s=58))
    band_handles = []
    for label, marker in marker_map.items():
        band_handles.append(ax.scatter([], [], color="#666666", marker=marker, label=label, s=58))
    ax.legend(handles=legend_handles + band_handles, loc="best", frameon=False, ncol=2)

    pca_plot_path = plots_dir / "protocol_v3_pca_projection.png"
    fig.savefig(pca_plot_path, dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 5), constrained_layout=True)
    raw_cv = stability["raw_pairwise_cv"]
    vector_cv = stability["vector_pairwise_cv"]
    scalar_cv = None
    if "scalar_pairwise_cv" in stability:
        scalar_cv = stability["scalar_pairwise_cv"]
    labels = ["Raw", "Vector"] + (["Scalar"] if scalar_cv is not None else [])
    values = [raw_cv, vector_cv] + ([scalar_cv] if scalar_cv is not None else [])
    colors = ["#9e9e9e", "#2f6fb2"] + (["#d97706"] if scalar_cv is not None else [])
    ax.bar(labels, values, color=colors)
    ax.set_title("Protocol V3 - coefficient of variation of pairwise material distances")
    ax.set_ylabel("CV")
    ax.grid(axis="y", alpha=0.25)
    cv_plot_path = plots_dir / "protocol_v3_cv_comparison.png"
    fig.savefig(cv_plot_path, dpi=160)
    plt.close(fig)

    return {
        "pca_projection": str(pca_plot_path),
        "cv_comparison": str(cv_plot_path),
    }


def build_summary(materials: list[dict], result_dir: Path) -> dict:
    geometry = full_geometry_test(materials)
    loo = leave_one_material_out(materials)
    regime = regime_continuity(materials)
    stability = stability_statistics(materials)
    vector_model = pca_fit(material_point_cloud(materials, "vector"))
    scalar = scalar_reduction(materials, vector_model)
    plots = make_plots(materials, {**geometry, "loo": loo, "regime": regime}, {**stability, **scalar}, result_dir)

    test0_supported = len(materials) >= len(REQUIRED_MATERIALS) and all(material["point_count"] == 5 for material in summarize_materials(materials))
    test0_reason = "The manifest exposes the four required materials and each series contains five points; DC is absent but the low-frequency anchor is present." if test0_supported else "The required material coverage is incomplete."

    tests = [
        {
            "id": "TEST0",
            "title": "Donnees et perimetre",
            "verdict": "supported" if test0_supported else "blocked",
            "reason": test0_reason,
            "metrics": {
                "required_materials": list(REQUIRED_MATERIALS),
                "optional_materials": list(OPTIONAL_MATERIALS),
                "material_count": len(materials),
                "point_count": sum(len(material["points"]) for material in materials),
                "bands_present": sorted({point["band"] for material in materials for point in material["points"]}),
            },
        },
        {
            "id": "TEST1",
            "title": "Construction de l espace invariant",
            "verdict": "supported",
            "reason": "Each point maps to a 2D invariant vector built from the amplitude ratio A = delta * sqrt(f) relative to a material anchor and the conductivity ratio to copper.",
            "metrics": {
                "vector_dimension": 2,
                "feature_names": ["log10(A/A_ref_material)", "sigma/sigma_Cu"],
                "vector_centroids": geometry["centroids"],
            },
        },
        {
            "id": "TEST2",
            "title": "Geometrie inter-materiaux",
            "verdict": geometry["verdict"],
            "reason": geometry["reason"],
            "metrics": {
                "separation_ratio": geometry["separation_ratio"],
                "raw_separation_ratio": geometry["raw_separation_ratio"],
                "pca_explained_variance_ratio": geometry["pca_explained_variance_ratio"],
                "pca_top2_explained": geometry["pca_top2_explained"],
                "nearest_neighbors": geometry["nearest_neighbors"],
            },
        },
        {
            "id": "TEST3",
            "title": "Leave-one-material-out",
            "verdict": loo["verdict"],
            "reason": loo["reason"],
            "metrics": {
                "folds": loo["folds"],
            },
        },
        {
            "id": "TEST4",
            "title": "Changement de regime",
            "verdict": regime["verdict"],
            "reason": regime["reason"],
            "metrics": {
                "coverage": regime["coverage"],
                "explicit_dc_available": regime["explicit_dc_available"],
                "band_pca_top2": regime["band_pca_top2"],
                "band_nearest_neighbors": regime["band_nearest_neighbors"],
                "band_mean_shift": regime["band_mean_shift"],
                "band_max_shift": regime["band_max_shift"],
            },
        },
        {
            "id": "TEST5",
            "title": "Stabilite statistique",
            "verdict": stability["verdict"],
            "reason": stability["reason"],
            "metrics": {
                "raw_pairwise_cv": stability["raw_pairwise_cv"],
                "vector_pairwise_cv": stability["vector_pairwise_cv"],
                "improvement_ratio": stability["improvement_ratio"],
                "leave_one_out_pairwise_cv": stability["leave_one_out_pairwise_cv"],
            },
        },
        {
            "id": "TEST6",
            "title": "Reduction scalaire optionnelle",
            "verdict": scalar["verdict"],
            "reason": scalar["reason"],
            "metrics": {
                "scalar_pairwise_cv": scalar["scalar_pairwise_cv"],
                "vector_pairwise_cv": scalar["vector_pairwise_cv"],
                "material_scalar_centroids": scalar["material_scalar_centroids"],
            },
        },
    ]

    core_supported = all(test["verdict"] == "supported" for test in tests[:5])
    if core_supported:
        overall_verdict = "supported" if tests[0]["verdict"] == "supported" else "partiel"
    else:
        overall_verdict = "contradicted" if not any(test["verdict"] == "supported" for test in tests[1:5]) else "partiel"

    supported_count = sum(1 for test in tests if test["verdict"] == "supported")
    return {
        "suite": "protocol_v3_vector",
        "timestamp": time.strftime("%Y%m%d-%H%M%SZ"),
        "overall_verdict": overall_verdict,
        "supported_count": supported_count,
        "total": len(tests),
        "tests": tests,
        "materials": summarize_materials(materials),
        "geometry": geometry,
        "leave_one_out": loo,
        "regime": regime,
        "stability": stability,
        "scalar": scalar,
        "plots": plots,
    }


def write_summary(summary: dict, result_dir: Path) -> dict:
    result_dir.mkdir(parents=True, exist_ok=True)
    timestamp = summary["timestamp"]
    json_path = result_dir / f"protocol_v3_vector_summary_{timestamp}.json"
    txt_path = result_dir / f"protocol_v3_vector_summary_{timestamp}.txt"
    md_path = result_dir / "protocole_v3_vectoriel.md"
    pca_plot_relative = Path(summary["plots"]["pca_projection"]).relative_to(result_dir).as_posix()
    cv_plot_relative = Path(summary["plots"]["cv_comparison"]).relative_to(result_dir).as_posix()

    payload = {**summary, "json_path": str(json_path), "txt_path": str(txt_path), "md_path": str(md_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "Protocol V3 vector summary",
        f"timestamp: {timestamp}",
        f"overall_verdict: {summary['overall_verdict']}",
        f"supported_count: {summary['supported_count']}/{summary['total']}",
        "",
        "Tests:",
    ]
    for test in summary["tests"]:
        lines.append(f"- {test['id']}: {test['verdict']} - {test['title']}")
        lines.append(f"  - {test['reason']}")
    lines.extend([
        "",
        "Geometry:",
        f"- raw separation ratio: {summary['geometry']['raw_separation_ratio']:.6f}",
        f"- vector separation ratio: {summary['geometry']['separation_ratio']:.6f}",
        f"- top2 PCA explained: {summary['geometry']['pca_top2_explained']:.6f}",
        "",
        "Stability:",
        f"- raw pairwise CV: {summary['stability']['raw_pairwise_cv']:.6f}",
        f"- vector pairwise CV: {summary['stability']['vector_pairwise_cv']:.6f}",
        f"- leave-one-out max CV: {max(summary['stability']['leave_one_out_pairwise_cv']):.6f}",
        "",
        "Plots:",
        f"- PCA projection: {summary['plots']['pca_projection']}",
        f"- CV comparison: {summary['plots']['cv_comparison']}",
    ])
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    md_lines = [
        "# Protocole V3 - Geometrie vectorielle",
        "",
        "## But",
        "Chercher une structure vectorielle stable dans les donnees HF sans fit global unique.",
        "",
        "## Verdict",
        f"- Verdict global: {summary['overall_verdict']}",
        f"- Tests supportes: {summary['supported_count']}/{summary['total']}",
        f"- Regimes disponibles: {', '.join(sorted(summary['regime']['coverage'].keys()))}",
        "",
        "## Test 0 - Perimetre",
        f"- {summary['tests'][0]['reason']}",
        "",
        "## Test 1 - Espace vectoriel",
        "- V = [log10(A/A_ref_material), sigma/sigma_Cu] avec A = delta * sqrt(f)",
        "- Le premier axe mesure l ecart d amplitude invariant dans chaque materiau; le second porte la conductivite relative.",
        "",
        "## Test 2 - Geometrie inter-materiaux",
        f"- Separation ratio brut: {summary['geometry']['raw_separation_ratio']:.6f}",
        f"- Separation ratio vectoriel: {summary['geometry']['separation_ratio']:.6f}",
        f"- PCA top2 expliquee: {summary['geometry']['pca_top2_explained']:.6f}",
        "",
        "## Test 3 - Leave-one-material-out",
        "- La geometrie est reconstruite sans le materiau laisse de cote puis comparee a son placement geometrique.",
        "",
        "## Test 4 - Changement de regime",
        f"- Couverture des bandes: {json.dumps(summary['regime']['coverage'], ensure_ascii=False)}",
        f"- Test de continuité par bandes: {summary['regime']['verdict']}",
        "",
        "## Test 5 - Stabilite statistique",
        f"- CV brut: {summary['stability']['raw_pairwise_cv']:.6f}",
        f"- CV vectoriel: {summary['stability']['vector_pairwise_cv']:.6f}",
        f"- Max CV leave-one-out: {max(summary['stability']['leave_one_out_pairwise_cv']):.6f}",
        "",
        "## Test 6 - Reduction scalaire optionnelle",
        f"- {summary['scalar']['reason']}",
        "",
        "## Plots",
        f"- [PCA projection]({pca_plot_relative})",
        f"- [CV comparison]({cv_plot_relative})",
        "",
        "## Lecture courte",
        "Le V3 privilegie la geometrie vectorielle. Le scalaire derivé n'est retenu que s'il ne degrage pas la stabilite inter-materiaux.",
    ]
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    summary.update({"json_path": str(json_path), "txt_path": str(txt_path), "md_path": str(md_path)})
    return summary


def run_suite(output_dir: str | Path | None = None) -> dict:
    root = workspace_root()
    result_dir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
    manifest = load_manifest(root)
    if str(manifest.get("status", "")).lower() != "ready":
        raise ValueError("HF transport manifest must be ready before running V3")
    materials = load_material_series(root)
    summary = build_summary(materials, result_dir)
    return write_summary(summary, result_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the protocol V3 vector-geometry suite on HF transport data.")
    parser.add_argument("--output-dir", default=None, help="Directory for the suite summary")
    args = parser.parse_args()

    result = run_suite(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()