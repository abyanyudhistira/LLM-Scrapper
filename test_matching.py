"""
Script untuk test matching profil dengan requirements
Gunakan data JSON yang sudah ada atau buat baru
"""

from app.main import process_candidate
import json

# Contoh 1: Test dengan data hardcoded
def test_with_sample_data():
    print("=== TEST 1: Sample Data ===\n")
    
    profile = {
        "name": "Jane Smith",
        "headline": "Full Stack Developer",
        "experiences": [
            {
                "title": "Full Stack Developer",
                "company": "Tech Startup",
                "duration_months": 24,
                "description": "Built web apps with React and Node.js"
            }
        ],
        "skills": ["JavaScript", "React", "Node.js", "MongoDB"],
        "education": [
            {
                "degree": "Bachelor of Computer Science",
                "institution": "University XYZ"
            }
        ]
    }
    
    requirement = {
        "job_title": "Frontend Developer",
        "company_name": "PT Digital Indonesia",
        "required_skills": ["React", "JavaScript", "CSS"],
        "min_experience_years": 2,
        "preferred_education": ["Bachelor of Computer Science"],
        "job_description": "Mencari frontend developer untuk membangun aplikasi web modern"
    }
    
    result = process_candidate(profile, requirement)
    print_result(result)


# Contoh 2: Test dengan file JSON
def test_with_json_files(profile_file=None, requirement_file=None):
    print(f"\n=== TEST 2: From JSON Files ===\n")
    
    # Jika tidak ada parameter, tampilkan pilihan file
    if not profile_file:
        profile_file = select_file_from_folder("data/profiles", "profil")
        if not profile_file:
            print("Tidak ada file profil yang dipilih.")
            return
    
    if not requirement_file:
        requirement_file = select_file_from_folder("data/requirements", "requirement")
        if not requirement_file:
            print("Tidak ada file requirement yang dipilih.")
            return
    
    with open(profile_file, 'r', encoding='utf-8') as f:
        profile = json.load(f)
    
    with open(requirement_file, 'r', encoding='utf-8') as f:
        requirement = json.load(f)
    
    result = process_candidate(profile, requirement)
    print_result(result)


def select_file_from_folder(folder_path, file_type):
    """Tampilkan list file JSON di folder dan biarkan user pilih"""
    import os
    from pathlib import Path
    
    # Buat folder jika belum ada
    Path(folder_path).mkdir(parents=True, exist_ok=True)
    
    # List semua file JSON di folder
    files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
    
    if not files:
        print(f"\nTidak ada file JSON di folder '{folder_path}'")
        print(f"Silakan tambahkan file {file_type} terlebih dahulu.")
        return None
    
    print(f"\n=== Pilih File {file_type.title()} ===")
    for i, file in enumerate(files, 1):
        print(f"{i}. {file}")
    
    while True:
        try:
            choice = input(f"\nPilih nomor (1-{len(files)}): ")
            idx = int(choice) - 1
            if 0 <= idx < len(files):
                selected_file = os.path.join(folder_path, files[idx])
                print(f"✓ Dipilih: {files[idx]}")
                return selected_file
            else:
                print(f"Pilih nomor antara 1-{len(files)}")
        except ValueError:
            print("Input tidak valid. Masukkan nomor.")
        except KeyboardInterrupt:
            print("\nDibatalkan.")
            return None


# Contoh 3: Test dengan input manual
def test_with_manual_input():
    print("\n=== TEST 3: Manual Input ===\n")
    print("Masukkan data profil kandidat:")
    
    name = input("Nama: ")
    headline = input("Headline: ")
    
    # Simplified input untuk demo
    profile = {
        "name": name,
        "headline": headline,
        "experiences": [
            {
                "title": input("Job Title terakhir: "),
                "company": input("Company terakhir: "),
                "duration_months": int(input("Durasi (bulan): ")),
                "description": input("Deskripsi pekerjaan: ")
            }
        ],
        "skills": input("Skills (pisahkan dengan koma): ").split(","),
        "education": [
            {
                "degree": input("Gelar pendidikan: "),
                "institution": input("Institusi: ")
            }
        ]
    }
    
    print("\nMasukkan requirements lowongan:")
    requirement = {
        "job_title": input("Posisi: "),
        "company_name": input("Nama perusahaan: "),
        "required_skills": input("Skills required (pisahkan dengan koma): ").split(","),
        "min_experience_years": int(input("Min pengalaman (tahun): ")),
        "job_description": input("Deskripsi pekerjaan: ")
    }
    
    result = process_candidate(profile, requirement)
    print_result(result)


def print_result(result):
    print("\n" + "="*50)
    print("HASIL MATCHING")
    print("="*50)
    print(f"Kandidat: {result['candidate_name']}")
    print(f"Posisi: {result['job_title']}")
    print(f"Score: {result['score']}/100")
    print(f"Kirim Pesan: {'Ya' if result['should_send_message'] else 'Tidak'}")
    print(f"\nSummary:\n{result['summary']}")
    print("\nDetail Requirements:")
    for req in result['matched_requirements']:
        status = "✓" if req['status'] == "terpenuhi" else "✗"
        print(f"{status} {req['requirement']}: {req['explanation']}")
    print("="*50 + "\n")


if __name__ == "__main__":
    import sys
    
    print("="*60)
    print("  LINKEDIN PROFILE MATCHER - TESTING TOOL")
    print("="*60)
    print("\nPILIH MODE TEST:")
    print("1. Test dengan sample data (quick test)")
    print("2. Test dengan file JSON (pilih dari folder)")
    print("3. Test dengan input manual")
    print("0. Keluar")
    
    choice = input("\nPilih (0/1/2/3): ")
    
    if choice == "1":
        test_with_sample_data()
    elif choice == "2":
        test_with_json_files()
    elif choice == "3":
        test_with_manual_input()
    elif choice == "0":
        print("Keluar.")
    else:
        print("Pilihan tidak valid")
