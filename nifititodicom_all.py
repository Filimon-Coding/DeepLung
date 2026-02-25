#### IMPORTS ###

'''
We are using:

OS -> file/folder read and write  
PyDICOM -> reads DICOM files 
Nibabel -> handels NiFti files like write and read 
Numpy  -> array manipulation
Path -> used to find Windows paths easier
Mathplotlib -> used to display the results in graphs
'''

import os
import pydicom
import nibabel as nib
import numpy as np
from pathlib import Path
from matplotlib import pyplot as plt


def convert_dicom_to_nifti(dicom_folder, output_path):
    try:
        print(f"Processing: {os.path.basename(dicom_folder)}")
        
        # Get all DICOM files
        dicom_files = sorted(Path(dicom_folder).glob("*.dcm"))
        
        if len(dicom_files) < 10:
            print(f" Only {len(dicom_files)} files, skipping")
            return False
        
        print(f"Reading {len(dicom_files)} DICOM slices...")
        
        slices = []
        slice_positions = []
        slice_thicknesses = []
        
        # Read all slices
        for i, dcm_file in enumerate(dicom_files):
            try:
                ds = pydicom.dcmread(dcm_file, force=True)
                
                # Get pixel data
                pixel_data = ds.pixel_array.astype(np.float32)
                
                # Apply rescale for CT (Hounsfield Units)
                if hasattr(ds, 'RescaleSlope') and hasattr(ds, 'RescaleIntercept'):
                    pixel_data = pixel_data * ds.RescaleSlope + ds.RescaleIntercept
                
                slices.append(pixel_data)
                
                # Get slice position for sorting
                if hasattr(ds, 'SliceLocation'):
                    slice_positions.append(float(ds.SliceLocation))
                else:
                    slice_positions.append(i)  # Fallback
                
                # Get slice thickness
                if hasattr(ds, 'SliceThickness'):
                    slice_thicknesses.append(float(ds.SliceThickness))
                
                if i == 0:  # Get metadata from first slice
                    first_ds = ds
                    
            except Exception as e:
                print(f"Error reading {dcm_file.name}: {e}")
                continue
        
        if not slices:
            print(f"No valid DICOM slices found")
            return False
        
        # Sort slices by position
        sorted_indices = np.argsort(slice_positions)
        volume = np.stack([slices[i] for i in sorted_indices], axis=-1)
        
        print(f"Volume shape: {volume.shape}")
        
        # Create affine matrix
        if hasattr(first_ds, 'PixelSpacing'):
            pixel_spacing = first_ds.PixelSpacing
        else:
            pixel_spacing = [1.0, 1.0]
        
        if slice_thicknesses:
            slice_thickness = np.mean(slice_thicknesses)
        else:
            slice_thickness = 1.0
        
        # Standard LPS to RAS affine for NIfTI
        affine = np.eye(4)
        affine[0, 0] = -pixel_spacing[0]  # X
        affine[1, 1] = -pixel_spacing[1]  # Y
        affine[2, 2] = slice_thickness     # Z
        
        # Create NIfTI image
        nifti_img = nib.Nifti1Image(volume, affine)
        
        # Add basic header info
        nifti_img.header['descrip'] = f'CT from {os.path.basename(dicom_folder)}'
        
        # Save
        nib.save(nifti_img, output_path)
        print(f"Saved: {os.path.basename(output_path)}")
        
        return True
        
    except Exception as e:
        print(f"Conversion failed: {str(e)[:100]}")
        return False

# MAIN CONVERSION SCRIPT
base_path = r"dataset/manifest-1600709154662/LIDC-IDRI"
output_dir = "./nifti_output_python"
os.makedirs(output_dir, exist_ok=True)

print(f"Base path: {os.path.abspath(base_path)}")
print(f"Output: {os.path.abspath(output_dir)}")
print("=" * 60)

# Process first 5 patients to test
success_count = 0

for i in range(1, 1013):  
    patient_id = f"LIDC-IDRI-{i:04d}"
    patient_folder = os.path.join(base_path, patient_id)
    
    print(f"\n{'='*50}")
    print(f"Patient: {patient_id}")
    
    if not os.path.exists(patient_folder):
        print(f"Folder not found")
        continue
    
    # Find ALL folders with DICOMs
    dicom_folders = []
    
    for root, dirs, files in os.walk(patient_folder):
        dcm_files = [f for f in files if f.lower().endswith('.dcm')]
        if dcm_files:
            dicom_folders.append((root, len(dcm_files)))
    
    if not dicom_folders:
        print(f"❌ No DICOM files found")
        continue
    
    # Show what we found
    print(f"Found {len(dicom_folders)} folder(s):")
    for folder, count in sorted(dicom_folders, key=lambda x: x[1], reverse=True):
        rel_path = os.path.relpath(folder, patient_folder)
        if count > 10:
            print(f"{rel_path}/ → {count} files (CT)")
        else:
            print(f"{rel_path}/ → {count} files (scout)")
    
    # Pick folder with most DICOMs
    dicom_folders.sort(key=lambda x: x[1], reverse=True)
    best_folder, file_count = dicom_folders[0]
    
    print(f"\nSelected: {os.path.basename(best_folder)} ({file_count} files)")
    
    # Convert if it's CT volume
    if file_count > 10:
        output_file = os.path.join(output_dir, f"{patient_id}_CT.nii.gz")
        
        if convert_dicom_to_nifti(best_folder, output_file):
            success_count += 1
            # Verify file was created
            if os.path.exists(output_file):
                size_mb = os.path.getsize(output_file) / (1024 * 1024)
                print(f"Verified: {size_mb:.1f} MB")
    else:
        print(f"Skipping: Likely scout ({file_count} files)")

print(f"\n{'='*60}")
print(f"Conversion complete!")
print(f"Successfully converted: {success_count} patients")
print(f"Output folder: {os.path.abspath(output_dir)}")

# List created files
print("\nCreated files:")
for f in sorted(Path(output_dir).glob("*.nii*")):
    size_mb = f.stat().st_size / (1024 * 1024)
    print(f"  {f.name} ({size_mb:.1f} MB)")
    
    

# --- Load DICOM files ---
dicom_folder = "dataset/manifest-1600709154662/LIDC-IDRI/LIDC-IDRI-0001/01-01-2000-NA-NA-30178/3000566.000000-NA-03192"
dicom_files = sorted([os.path.join(dicom_folder, f) for f in os.listdir(dicom_folder) if f.endswith('.dcm')])

# Read all slices and stack them into a 3D array
dicom_slices = [pydicom.dcmread(f).pixel_array for f in dicom_files]
dicom_volume = np.stack(dicom_slices, axis=-1)  # Shape: (height, width, num_slices)

# --- Load NIfTI file ---
nifti_file = "nifti_output_python/LIDC-IDRI-0001_CT.nii.gz"
nifti_img = nib.load(nifti_file)
nifti_data = nifti_img.get_fdata()  # Shape: (height, width, num_slices) or similar

# --- Plot comparison ---
slice_idx = dicom_volume.shape[-1] // 2  # middle slice
plt.figure(figsize=(10, 5))

# DICOM slice
plt.subplot(1, 2, 1)
plt.imshow(dicom_volume[:, :, slice_idx], cmap='gray')
plt.title('DICOM Middle Slice')
plt.axis('off')

# NIfTI slice
plt.subplot(1, 2, 2)
plt.imshow(nifti_data[:, :, slice_idx], cmap='gray')
plt.title('NIfTI Middle Slice')
plt.axis('off')

plt.show()
