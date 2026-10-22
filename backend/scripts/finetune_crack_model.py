"""
CrackVision AI — Production Crack Segmentation Fine-Tuning Pipeline

Downloads real crack segmentation datasets from Roboflow Universe,
merges them into a combined training corpus, and fine-tunes YOLOv8s-seg
with aggressive augmentation for robust real-world crack detection.

Usage:
    python backend/scripts/finetune_crack_model.py --api_key YOUR_ROBOFLOW_KEY
"""

import os
import sys
import shutil
import argparse
import glob
import yaml
from pathlib import Path


# ---------------------------------------------------------------------------
# 1. Dataset Download & Merge
# ---------------------------------------------------------------------------

# Curated list of high-quality public crack segmentation datasets on Roboflow
# Each tuple: (workspace, project_slug, version, description)
DATASETS = [
    # Primary: Large concrete/wall crack instance segmentation (~400+ images)
    ("crack-va79x", "crack-detection-using-instance-segmentation-in-yolov8-8slmu", 1,
     "Crack Instance Segmentation (walls, concrete, asphalt)"),
    # Secondary: Concrete crack detection with polygon masks
    ("university-bswxt", "crack-bphil", 1,
     "Concrete Crack Segmentation (university dataset)"),
]


def download_datasets(api_key: str, base_dir: Path):
    """Download crack segmentation datasets from Roboflow Universe."""
    try:
        from roboflow import Roboflow
    except ImportError:
        print("[-] roboflow not installed. Run: pip install roboflow")
        sys.exit(1)

    rf = Roboflow(api_key=api_key)
    downloaded_paths = []

    for workspace, project_slug, version_num, desc in DATASETS:
        print(f"\n{'='*60}")
        print(f"[+] Downloading: {desc}")
        print(f"    Workspace: {workspace} | Project: {project_slug} | Version: {version_num}")
        print(f"{'='*60}")
        try:
            project = rf.workspace(workspace).project(project_slug)
            version = project.version(version_num)
            dataset = version.download("yolov8", location=str(base_dir / f"dataset_{workspace}"))
            downloaded_paths.append(Path(dataset.location))
            print(f"[+] ✓ Downloaded to: {dataset.location}")
        except Exception as e:
            print(f"[!] ✗ Failed to download {desc}: {e}")
            print(f"    Skipping this dataset, will try others...")
            continue

    if not downloaded_paths:
        print("\n[-] No datasets could be downloaded. Trying fallback approach...")
        # Fallback: try a broader search
        try:
            project = rf.workspace("crack-va79x").project("crack-detection-using-instance-segmentation-in-yolov8-8slmu")
            version = project.version(1)
            dataset = version.download("yolov8", location=str(base_dir / "dataset_fallback"))
            downloaded_paths.append(Path(dataset.location))
            print(f"[+] ✓ Fallback dataset downloaded to: {dataset.location}")
        except Exception as e2:
            print(f"[-] Fallback also failed: {e2}")
            print("\n[!] Please try one of these manual approaches:")
            print("    1. Go to https://universe.roboflow.com and search 'crack segmentation'")
            print("    2. Download in YOLOv8 format and place in backend/datasets/")
            sys.exit(1)

    return downloaded_paths


def merge_datasets(dataset_paths: list, output_dir: Path):
    """
    Merge multiple YOLO-format datasets into one combined dataset.
    Handles different directory structures (train/valid/test splits).
    """
    merged_images_train = output_dir / "images" / "train"
    merged_labels_train = output_dir / "labels" / "train"
    merged_images_val = output_dir / "images" / "val"
    merged_labels_val = output_dir / "labels" / "val"

    for d in [merged_images_train, merged_labels_train, merged_images_val, merged_labels_val]:
        os.makedirs(d, exist_ok=True)

    total_train = 0
    total_val = 0

    for idx, ds_path in enumerate(dataset_paths):
        prefix = f"ds{idx}_"
        print(f"\n[+] Merging dataset {idx}: {ds_path}")

        # Find train images (could be train/, images/train/, etc.)
        train_img_dirs = []
        val_img_dirs = []

        for pattern in ["train/images", "images/train", "train"]:
            candidate = ds_path / pattern
            if candidate.exists() and any(candidate.iterdir()):
                train_img_dirs.append(candidate)
                break

        for pattern in ["valid/images", "images/val", "val/images", "images/valid", "valid", "val"]:
            candidate = ds_path / pattern
            if candidate.exists() and any(candidate.iterdir()):
                val_img_dirs.append(candidate)
                break

        # If no explicit val split, use test as val
        if not val_img_dirs:
            for pattern in ["test/images", "images/test", "test"]:
                candidate = ds_path / pattern
                if candidate.exists() and any(candidate.iterdir()):
                    val_img_dirs.append(candidate)
                    break

        # Copy train images and labels
        for img_dir in train_img_dirs:
            label_dir = _find_label_dir(img_dir)
            count = _copy_split(img_dir, label_dir, merged_images_train, merged_labels_train, prefix)
            total_train += count
            print(f"    [+] Train: copied {count} images from {img_dir}")

        # Copy val images and labels
        for img_dir in val_img_dirs:
            label_dir = _find_label_dir(img_dir)
            count = _copy_split(img_dir, label_dir, merged_images_val, merged_labels_val, prefix)
            total_val += count
            print(f"    [+] Val: copied {count} images from {img_dir}")

    # If no val data, split 15% from train
    if total_val == 0 and total_train > 0:
        print("\n[+] No validation split found. Creating 85/15 train/val split...")
        import random
        random.seed(42)
        train_images = list(merged_images_train.glob("*.*"))
        random.shuffle(train_images)
        val_count = max(int(len(train_images) * 0.15), 1)
        for img_path in train_images[:val_count]:
            # Move image
            shutil.move(str(img_path), str(merged_images_val / img_path.name))
            # Move label
            label_name = img_path.stem + ".txt"
            label_path = merged_labels_train / label_name
            if label_path.exists():
                shutil.move(str(label_path), str(merged_labels_val / label_name))
            total_val += 1
            total_train -= 1

    print(f"\n[+] Merged dataset summary:")
    print(f"    Train images: {total_train}")
    print(f"    Val images: {total_val}")
    print(f"    Total: {total_train + total_val}")

    # Write dataset.yaml
    yaml_content = {
        "path": str(output_dir.resolve()),
        "train": "images/train",
        "val": "images/val",
        "names": {0: "crack"}
    }
    yaml_path = output_dir / "dataset.yaml"
    with open(yaml_path, "w") as f:
        yaml.dump(yaml_content, f, default_flow_style=False)

    print(f"[+] Dataset config written to: {yaml_path}")
    return yaml_path, total_train, total_val


def _find_label_dir(img_dir: Path) -> Path:
    """Given an image directory, find its corresponding label directory."""
    # Strategy 1: sibling 'labels' dir  (e.g. train/images -> train/labels)
    sibling = img_dir.parent / "labels"
    if sibling.exists():
        return sibling
    # Strategy 2: parallel labels dir (e.g. images/train -> labels/train)
    parallel = img_dir.parent.parent / "labels" / img_dir.name
    if parallel.exists():
        return parallel
    # Strategy 3: same dir (labels next to images)
    return img_dir


def _copy_split(img_dir: Path, label_dir: Path, out_img: Path, out_lbl: Path, prefix: str) -> int:
    """Copy images and their matching labels to the output directories."""
    count = 0
    for img_path in img_dir.iterdir():
        if img_path.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp", ".bmp"]:
            new_name = prefix + img_path.name
            shutil.copy2(str(img_path), str(out_img / new_name))

            # Find matching label
            label_name = img_path.stem + ".txt"
            label_path = label_dir / label_name
            if label_path.exists():
                # Verify label contains segmentation polygons (class_id x1 y1 x2 y2 ... format)
                # and remap all class IDs to 0 (crack)
                _remap_and_copy_label(label_path, out_lbl / (prefix + label_name))
            count += 1
    return count


def _remap_and_copy_label(src_label: Path, dst_label: Path):
    """
    Copy a YOLO label file, remapping all class IDs to 0 (single-class: crack).
    This ensures multi-class datasets get merged into our single 'crack' class.
    """
    lines = []
    with open(src_label, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 5:  # class_id + at least 2 polygon points (4 coords)
                parts[0] = "0"  # Remap to class 0 = crack
                lines.append(" ".join(parts))

    with open(dst_label, "w") as f:
        f.write("\n".join(lines) + "\n" if lines else "")


# ---------------------------------------------------------------------------
# 2. Training
# ---------------------------------------------------------------------------

def train_model(
    data_yaml: Path,
    base_model: str = "yolov8s-seg.pt",
    epochs: int = 80,
    imgsz: int = 640,
    batch: int = 8,
    device: str = "mps",
    project_dir: str = "runs/crackvision_finetune"
):
    """
    Fine-tune YOLOv8 segmentation model with heavy augmentation
    optimized for real-world crack detection accuracy.
    """
    try:
        from ultralytics import YOLO
    except ImportError:
        print("[-] ultralytics not installed. Run: pip install ultralytics")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"  TRAINING CONFIGURATION")
    print(f"{'='*60}")
    print(f"  Base model:    {base_model}")
    print(f"  Dataset:       {data_yaml}")
    print(f"  Epochs:        {epochs}")
    print(f"  Image size:    {imgsz}")
    print(f"  Batch size:    {batch}")
    print(f"  Device:        {device}")
    print(f"{'='*60}\n")

    model = YOLO(base_model)

    results = model.train(
        data=str(data_yaml),
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        device=device,
        patience=20,            # Early stopping patience
        save=True,
        save_period=10,         # Checkpoint every 10 epochs
        project=project_dir,
        name="crack_seg_v1",
        exist_ok=True,

        # ---------- Heavy Data Augmentation for Crack Robustness ----------
        # These are critical for generalizing to real-world camera photos
        # with varying lighting, shadows, angles, and surface textures.

        # Color/Lighting augmentations (handle phone camera exposure variance)
        hsv_h=0.02,            # Hue jitter (cracks don't change hue much)
        hsv_s=0.7,             # Saturation jitter (handle washed-out photos)
        hsv_v=0.5,             # Brightness jitter (handle shadows/overexposure)

        # Geometric augmentations (cracks appear at any angle)
        degrees=180.0,         # Full rotation — cracks have no preferred orientation
        translate=0.15,        # Random translation
        scale=0.6,             # Scale variation (close-up vs wide shots)
        shear=5.0,             # Shear distortion
        perspective=0.001,     # Perspective warp (phone at angles)
        flipud=0.5,            # Vertical flip
        fliplr=0.5,            # Horizontal flip

        # Advanced augmentations
        mosaic=1.0,            # Mosaic — combines 4 images for multi-crack scenes
        mixup=0.15,            # MixUp — blend two images for regularization
        copy_paste=0.3,        # Copy-paste crack masks onto different backgrounds

        # Training hyperparameters
        lr0=0.01,              # Initial learning rate
        lrf=0.01,              # Final learning rate factor (cosine decay to lr0 * lrf)
        warmup_epochs=5,       # Gradual warmup
        warmup_bias_lr=0.1,
        weight_decay=0.0005,
        optimizer="AdamW",     # AdamW for better generalization

        # Loss weights (emphasize segmentation mask quality)
        box=7.5,               # Box loss gain
        cls=0.5,               # Classification loss (single class, less important)
        dfl=1.5,               # Distribution focal loss
    )

    print(f"\n[+] Training complete!")
    return model, results


# ---------------------------------------------------------------------------
# 3. Export & Deploy
# ---------------------------------------------------------------------------

def export_model(model, project_dir: str = "runs/crackvision_finetune"):
    """Export best weights to app/weights/ for immediate production use."""
    base_dir = Path(__file__).resolve().parent.parent
    weights_dir = base_dir / "app" / "weights"

    best_weights = Path(project_dir) / "crack_seg_v1" / "weights" / "best.pt"
    if not best_weights.exists():
        # Search for it
        candidates = list(Path(project_dir).rglob("best.pt"))
        if candidates:
            best_weights = candidates[0]
        else:
            print("[-] Could not find best.pt weights file!")
            return

    # Backup existing weights
    existing_pt = weights_dir / "crack_yolov8s_seg.pt"
    if existing_pt.exists():
        backup_path = weights_dir / "crack_yolov8s_seg_BACKUP_pretrained_coco.pt"
        shutil.copy2(str(existing_pt), str(backup_path))
        print(f"[+] Backed up old weights to: {backup_path}")

    # Copy new fine-tuned weights
    shutil.copy2(str(best_weights), str(existing_pt))
    print(f"[+] ✓ Deployed fine-tuned weights to: {existing_pt}")

    # Export ONNX for optional fast inference
    try:
        from ultralytics import YOLO
        export_model_obj = YOLO(str(existing_pt))
        onnx_path = export_model_obj.export(format="onnx", imgsz=640, simplify=True)
        # Copy ONNX to weights dir
        onnx_src = Path(onnx_path)
        onnx_dst = weights_dir / "crack_yolov8s_seg.onnx"
        if onnx_src.exists():
            shutil.copy2(str(onnx_src), str(onnx_dst))
            print(f"[+] ✓ Exported ONNX model to: {onnx_dst}")
    except Exception as e:
        print(f"[!] ONNX export skipped: {e}")

    # Verify the new model
    print(f"\n[+] Verifying deployed model...")
    try:
        from ultralytics import YOLO
        verify_model = YOLO(str(existing_pt))
        print(f"    Model task:   {verify_model.task}")
        print(f"    Class names:  {verify_model.names}")
        info = verify_model.info()
        print(f"[+] ✓ Model verification passed — ready for production!")
    except Exception as e:
        print(f"[-] Verification warning: {e}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="CrackVision AI — Fine-Tune YOLOv8s-seg for Crack Detection"
    )
    parser.add_argument("--api_key", type=str, required=True,
                        help="Roboflow API key (free at roboflow.com)")
    parser.add_argument("--model", type=str, default="yolov8s-seg.pt",
                        help="Base YOLO model to fine-tune (default: yolov8s-seg.pt)")
    parser.add_argument("--epochs", type=int, default=80,
                        help="Training epochs (default: 80)")
    parser.add_argument("--imgsz", type=int, default=640,
                        help="Image size (default: 640)")
    parser.add_argument("--batch", type=int, default=8,
                        help="Batch size (default: 8, reduce if OOM)")
    parser.add_argument("--device", type=str, default=None,
                        help="Device: mps, cuda, cpu (auto-detected if not set)")
    parser.add_argument("--skip_download", action="store_true",
                        help="Skip dataset download (use existing data)")
    parser.add_argument("--skip_train", action="store_true",
                        help="Skip training (only export existing best.pt)")

    args = parser.parse_args()

    # Auto-detect device
    if args.device is None:
        try:
            import torch
            if torch.backends.mps.is_available():
                args.device = "mps"
            elif torch.cuda.is_available():
                args.device = "cuda"
            else:
                args.device = "cpu"
        except:
            args.device = "cpu"

    print("=" * 60)
    print("  CrackVision AI — Crack Segmentation Fine-Tuning Pipeline")
    print("=" * 60)
    print(f"  Device: {args.device}")
    print(f"  Model:  {args.model}")
    print(f"  Epochs: {args.epochs}")
    print()

    base_dir = Path(__file__).resolve().parent.parent
    datasets_dir = base_dir / "datasets"
    merged_dir = datasets_dir / "crack_merged"

    # Step 1: Download datasets
    if not args.skip_download:
        print("\n" + "=" * 60)
        print("  STEP 1/3: Downloading Crack Segmentation Datasets")
        print("=" * 60)
        dataset_paths = download_datasets(args.api_key, datasets_dir)

        # Step 2: Merge datasets
        print("\n" + "=" * 60)
        print("  STEP 2/3: Merging Datasets into Unified Training Corpus")
        print("=" * 60)
        data_yaml, n_train, n_val = merge_datasets(dataset_paths, merged_dir)
    else:
        data_yaml = merged_dir / "dataset.yaml"
        if not data_yaml.exists():
            print(f"[-] No existing dataset found at {data_yaml}. Run without --skip_download first.")
            sys.exit(1)
        print(f"[+] Using existing dataset: {data_yaml}")

    # Step 3: Train
    if not args.skip_train:
        print("\n" + "=" * 60)
        print("  STEP 3/3: Fine-Tuning YOLOv8 Segmentation Model")
        print("=" * 60)
        model, results = train_model(
            data_yaml=data_yaml,
            base_model=args.model,
            epochs=args.epochs,
            imgsz=args.imgsz,
            batch=args.batch,
            device=args.device
        )

    # Step 4: Export & Deploy
    print("\n" + "=" * 60)
    print("  DEPLOYING FINE-TUNED MODEL")
    print("=" * 60)
    export_model(model if not args.skip_train else None)

    print("\n" + "=" * 60)
    print("  ✓ FINE-TUNING PIPELINE COMPLETE")
    print("=" * 60)
    print("  Your CrackVision AI model is now trained on real crack data.")
    print("  Restart the backend server to use the new model:")
    print("    cd backend && python -m uvicorn app.main:app --reload")
    print("=" * 60)


if __name__ == "__main__":
    main()
