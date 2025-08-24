
# Falling Sand — CI로 Windows .EXE 자동 생성

이 리포는 **GitHub Actions**가 자동으로 `FallingSand.exe`를 빌드해서
아티팩트로 제공하도록 구성돼 있어요.

## 사용법 (2분)
1. 새 깃허브 리포지토리 만들기 → 이 ZIP 안의 파일들을 그대로 업로드 (루트에 넣기)
2. 업로드 후 자동으로 워크플로가 돌거나, `Actions` 탭에서 **Run workflow** 눌러 수동 실행
3. 완료되면 `Actions` → 해당 실행 클릭 → **Artifacts**에서 `FallingSand-exe` 다운로드
4. 압축 풀면 `FallingSand.exe` (싱글플레이, 멀티X). 더블클릭 실행!

구성
- `sandbox_single.py` — 게임 본체 (Pygame)
- `requirements.txt` — 의존성
- `.github/workflows/build-windows.yml` — Windows VM에서 PyInstaller로 빌드 후 아티팩트 업로드

팁
- 아이콘 넣고 싶으면 `.ico` 파일 추가 후:
  `pyinstaller --noconsole --onefile --icon icon.ico --name FallingSand sandbox_single.py`
- 창 크기/해상도/요소 추가 등 커스텀 원하면 언제든 요청해줘요.
