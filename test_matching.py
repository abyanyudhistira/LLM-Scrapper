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
def test_with_json_files(profile_file, requirement_file):
    print(f"\n=== TEST 2: From JSON Files ===\n")
    
    with open(profile_file, 'r', encoding='utf-8') as f:
        profile = json.load(f)
    
    with open(requirement_file, 'r', encoding='utf-8') as f:
        requirement = json.load(f)
    
    result = process_candidate(profile, requirement)
    print_result(result)


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
    
    print("PILIH MODE TEST:")
    print("1. Test dengan sample data")
    print("2. Test dengan file JSON")
    print("3. Test dengan input manual")
    
    choice = input("\nPilih (1/2/3): ")
    
    if choice == "1":
        test_with_sample_data()
    elif choice == "2":
        profile_file = input("Path file profil JSON: ")
        requirement_file = input("Path file requirement JSON: ")
        test_with_json_files(profile_file, requirement_file)
    elif choice == "3":
        test_with_manual_input()
    else:
        print("Pilihan tidak valid")
