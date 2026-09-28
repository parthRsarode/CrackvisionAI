"""
CrackVision AI — Multi-Dataset YOLOv8/YOLOv11 Segmentation Training Script

This script automates downloading, combining, and fine-tuning YOLO segmentation models
on public crack datasets (Roboflow Universe, Crack500, DeepCrack, SDNET2018).

Usage:
    1. Activate python environment:
       source backend/venv/bin/activate
    2. Install dependencies:
       pip install ultralytics roboflow opencv-python-headless albumentations
    3. Run training:
       python backend/scripts/train_yolo.py --model yolov8s-seg.pt --epochs 50 --imgsz 640
"""

import os
import sys
import argparse
import shutil
from pathlib import Path

def setup_multidataset_config():
    """
    Generate dataset.yaml for combined multi-dataset training.
    """
    base_dir = Path(__file__).resolve().parent.parent
    dataset_dir = base_dir / "datasets" / "crack_combined"
    os.makedirs(dataset_dir / "images" / "train", exist_ok=True)
    os.makedirs(dataset_dir / "images" / "val", exist_ok=True)
    os.makedirs(dataset_dir / "labels" / "train", exist_ok=True)
    os.makedirs(dataset_dir / "labels" / "val", exist_ok=True)

    yaml_content = f"""# CrackVision AI Multi-Dataset Configuration
path: {dataset_dir.as_posix()}
train: images/train
val: images/val

names:
  0: crack
"""
    yaml_path = dataset_dir / "dataset.yaml"
    with open(yaml_path, "w") as f:
        f.write(yaml_content)
    
    print(f"[+] Created combined dataset configuration at: {yaml_path}")
    return yaml_path

def download_roboflow_dataset(api_key: str = None):
    """
    Download Crack Instance Segmentation dataset from Roboflow Universe if API key provided.
    """
    if not api_key:
        print("[!] No Roboflow API key provided. Skipping automatic Roboflow download.")
        print("    You can download public crack datasets from:")
        print("    1. Roboflow Universe: https://universe.roboflow.com/search?q=crack+segmentation")
        print("    2. Crack500: https://github.com/DYH29/CRACK500")
        print("    3. DeepCrack: https://github.com/yhlleo/DeepCrack")
        return None

    try:
        from roboflow import Roboflow
        rf = Roboflow(api_key=api_key)
        project = rf.workspace("crack-segmentation").project("concrete-crack-detection")
        dataset = project.download("yolov8-segmentation")
        print(f"[+] Downloaded Roboflow dataset to: {dataset.location}")
        return dataset.location
    except Exception as e:
        print(f"[-] Roboflow download error: {e}")
        return None

def train_model(data_yaml: Path, model_name: str = "yolov8s-seg.pt", epochs: int = 50, imgsz: int = 640):
    """
    Fine-tune YOLO segmentation model with heavy augmentations for high accuracy on diverse surfaces.
    """
    try:
        from ultralytics import YOLO
    except ImportError:
        print("[-] Ultralytics package not installed. Run: pip install ultralytics")
        sys.exit(1)

    print(f"[+] Initializing training with base model: {model_name}")
    model = YOLO(model_name)

    # Advanced Data Augmentations to boost accuracy on low-contrast concrete/asphalt cracks
    results = model.train(
        data=str(data_yaml),
        epochs=epochs,
        imgsz=imgsz,
        batch=16,
        patience=15,
        save=True,
        project="runs/crackvision_train",
        name="yolov8_crack_high_acc",
        # Data Augmentations
        hsv_h=0.015,     # HSV hue jitter
        hsv_s=0.7,       # HSV saturation jitter
        hsv_v=0.4,       # HSV value/brightness jitter
        degrees=15.0,    # Random rotation
        translate=0.1,   # Random translation
        scale=0.5,       # Random scaling
        shear=5.0,       # Shear angle
        perspective=0.0005, # Perspective distortion
        flipud=0.5,      # Vertical flip (cracks can be any orientation)
        fliplr=0.5,      # Horizontal flip
        mosaic=1.0,      # Mosaic augmentation for multi-crack scenes
        mixup=0.15,      # Mixup blending
        copy_paste=0.3,  # Copy-paste crack masks on background
    )

    print("[+] Fine-tuning complete!")
    
    # Save export weights to app models directory
    base_dir = Path(__file__).resolve().parent.parent
    output_model_dir = base_dir / "app" / "models"
    os.makedirs(output_model_dir, exist_ok=True)
    
    best_weights = Path("runs/crackvision_train/yolov8_crack_high_acc/weights/best.pt")
    if best_weights.exists():
        target_path = output_model_dir / "yolov8_crack_seg.pt"
        shutil.copy(best_weights, target_path)
        print(f"[+] Exported best model weights to: {target_path}")

        # Also export to ONNX format for fast inference without PyTorch binary dependency
        try:
            exported_onnx = model.export(format="onnx")
            print(f"[+] Exported ONNX model to: {exported_onnx}")
        except Exception as e:
            print(f"[!] ONNX export warning: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CrackVision AI YOLO Segmentation Model Trainer")
    parser.add_argument("--model", type=str, default="yolov8s-seg.pt", help="Base model (yolov8n-seg.pt, yolov8s-seg.pt, yolov8m-seg.pt)")
    parser.add_argument("--epochs", type=int, default=50, help="Number of training epochs")
    parser.add_argument("--imgsz", type=int, default=640, help="Image resolution for training")
    parser.add_argument("--roboflow_key", type=str, default=None, help="Optional Roboflow API key to auto-download dataset")
    
    args = parser.parse_args()

    print("==================================================")
    print("  CrackVision AI — Multi-Dataset Model Trainer")
    print("==================================================")

    yaml_path = setup_multidataset_config()
    rf_location = download_roboflow_dataset(args.roboflow_key)
    
    # Prompt for training if data is populated
    print("\n[+] Dataset configuration ready.")
    print("    Place your training images into: backend/datasets/crack_combined/images/train/")
    print("    Place your polygon label files into: backend/datasets/crack_combined/labels/train/")
    print(f"    Then run: python backend/scripts/train_yolo.py --epochs {args.epochs}")
