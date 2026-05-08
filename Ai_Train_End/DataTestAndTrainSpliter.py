def create_short_dataset(file_list, target_count=100):
    counts = {"Malignancy": 0, "Benign": 0}
    print(f"--- Starting Data Sorting: Target is {target_count} of each class ---")
    
    for fname in file_list:
        if counts["Malignancy"] >= target_count and counts["Benign"] >= target_count:
            print(f"--- Goal reached: {counts['Malignancy']} Malignant and {counts['Benign']} Benign images collected ---")
            break
            
        try:
            case_id = int(fname.split('-')[-1].split('_')[0])
        except:
            continue

        label_folder = "Malignancy" if case_id in cancer_cases else "Benign"
        
        if counts[label_folder] < target_count:
            subset = "Train" if (counts["Malignancy"] + counts["Benign"]) % 5 != 0 else "Test"
            dest_path = DATA_DIR / subset / label_folder
            dest_path.mkdir(parents=True, exist_ok=True)

            if not (dest_path / fname).exists():
                shutil.copy(INPUT_DIR / fname, dest_path / fname)
            
            counts[label_folder] += 1
            
            if (counts["Malignancy"] + counts["Benign"]) % 20 == 0:
                print(f"[DATA SETUP] Current Count -> Malignant: {counts['Malignancy']} | Benign: {counts['Benign']}")

# Check if data already exists, if not, create it
if not DATA_DIR.exists():
    create_short_dataset(all_files, target_count=100)
else:
    print(f"--- Folder '{DATA_DIR}' already exists. Skipping sorting. ---")