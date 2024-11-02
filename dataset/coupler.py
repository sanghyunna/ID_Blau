import os
import shutil

def create_image_pairs_with_deletion(clean_dir, noisy_dir, output_clean_dir, output_noisy_dir):
    # 출력 디렉토리가 없으면 생성합니다.
    os.makedirs(output_clean_dir, exist_ok=True)
    os.makedirs(output_noisy_dir, exist_ok=True)

    # 깨끗한 이미지 경로를 수집하고 ID를 추출하여 딕셔너리에 저장합니다.
    clean_image_paths = [os.path.join(clean_dir, x) for x in os.listdir(clean_dir) if x.lower().endswith(('.png', '.jpg', '.jpeg'))]
    clean_id_to_path = {}
    for clean_path in clean_image_paths:
        filename = os.path.basename(clean_path)
        clean_id = '_'.join(filename.split('_')[:-1])
        clean_id_to_path[clean_id] = clean_path

    # 깨끗한 이미지 참조 카운트를 저장하기 위한 딕셔너리
    clean_path_ref_count = {}

    # 노이즈 이미지 경로를 수집하고, ID를 추출하여 깨끗한 이미지와 매칭합니다.
    noisy_image_paths = [os.path.join(noisy_dir, x) for x in os.listdir(noisy_dir) if x.lower().endswith(('.png', '.jpg', '.jpeg'))]
    pairs = []
    for noisy_path in noisy_image_paths:
        filename = os.path.basename(noisy_path)
        noisy_id = '_'.join(filename.split('_')[:-1])
        if noisy_id in clean_id_to_path:
            clean_path = clean_id_to_path[noisy_id]
            pairs.append((noisy_path, clean_path))

            # 깨끗한 이미지의 참조 카운트를 증가시킵니다.
            if clean_path in clean_path_ref_count:
                clean_path_ref_count[clean_path] += 1
            else:
                clean_path_ref_count[clean_path] = 1

    # 쌍을 순회하면서 파일을 복사 및 이름 변경하고, 원본 파일을 삭제합니다.
    for idx, (noisy_path, clean_path) in enumerate(pairs, start=1):
        new_noisy_name = f"{idx}.jpg"
        new_clean_name = f"{idx}.jpg"

        # 노이즈 이미지 복사 및 이름 변경
        shutil.copy2(noisy_path, os.path.join(output_noisy_dir, new_noisy_name))
        # 원본 노이즈 이미지 삭제
        os.remove(noisy_path)

        # 깨끗한 이미지 복사 및 이름 변경
        shutil.copy2(clean_path, os.path.join(output_clean_dir, new_clean_name))

        # 깨끗한 이미지의 참조 카운트를 감소시킵니다.
        clean_path_ref_count[clean_path] -= 1
        # 참조 카운트가 0이면 원본 깨끗한 이미지 삭제
        if clean_path_ref_count[clean_path] == 0:
            os.remove(clean_path)

    # 모든 처리가 끝난 후, 빈 디렉토리 삭제
    try:
        os.rmdir(clean_dir)
    except OSError as e:
            print(f"디렉토리 삭제 오류: {e}")
    
    try:
        os.rmdir(noisy_dir)
    except OSError as e:
            print(f"디렉토리 삭제 오류: {e}")

    print(f"총 {len(pairs)}개의 이미지 쌍이 생성되고 원본 파일이 삭제되었습니다.")

if __name__ == "__main__":
    # 원본 이미지 디렉토리 경로를 지정합니다.
    clean_dir = "./clean"
    noisy_dir = "./noisy"

    # 출력 이미지 디렉토리 경로를 지정합니다.
    output_clean_dir = "./clean_output"
    output_noisy_dir = "./noisy_output"

    create_image_pairs_with_deletion(clean_dir, noisy_dir, output_clean_dir, output_noisy_dir)
