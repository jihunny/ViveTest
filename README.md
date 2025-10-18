다음은 uv로 가상 환경을 만들고 git과 gh로 GitHub에 새 프로젝트를 올리는 전체 순서입니다.

1. 프로젝트 폴더 생성 및 이동
먼저, 새로운 프로젝트를 담을 디렉터리(폴더)를 만들고 그 안으로 이동합니다.

Bash

mkdir my_project
cd my_project
2. uv 가상 환경 생성
uv를 사용해 .venv라는 이름의 가상 환경을 생성합니다.

Bash

uv venv
3. git 초기화 및 .gitignore 설정
Git 저장소를 초기화하고, 방금 만든 가상 환경 폴더(.venv)를 Git이 추적하지 않도록 .gitignore 파일을 설정합니다. 이 순서가 매우 중요합니다.

Bash

# 1. Git 저장소 초기화
git init

# 2. .gitignore 파일 생성 (가상 환경 폴더 무시)
#    (Windows에서는 echo ".venv/" > .gitignore)
echo ".venv/" > .gitignore

# 3. (선택 사항) Python 캐시 파일 등도 추가
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
4. uv 가상 환경 활성화
생성한 가상 환경을 활성화하여 이 터미널 세션에서 사용하도록 설정합니다.

macOS / Linux (bash/zsh):

Bash

source .venv/bin/activate
Windows (PowerShell):

Bash

.venv\Scripts\Activate.ps1
(활성화되면 터미널 프롬프트 앞에 (.venv)가 표시됩니다.)

5. 프로젝트 파일 생성 및 첫 커밋
이제 프로젝트의 기본 파일들을 생성하고 첫 번째 커밋(저장)을 만듭니다.

Bash

# 1. (예시) README 파일 생성
echo "# 나의 새 프로젝트" > README.md

# 2. (예시) 패키지 설치 및 requirements.txt 생성
uv pip install ruff flask
uv pip freeze > requirements.txt

# 3. 모든 변경 사항을 Git에 추가 (staging)
# (.gitignore, README.md, requirements.txt 등이 추가됨)
git add .

# 4. 첫 번째 커밋 생성
git commit -m "Initial commit"
6. gh로 GitHub 리포지토리 생성 및 푸시
gh (GitHub CLI) 명령어를 사용하여 GitHub에 새 리포지토리를 만들고, 방금 커밋한 내용을 한 번에 푸시합니다.

Bash

# 'my_project'라는 이름의 공개 리포지토리를 만들고,
# 현재 폴더 내용을 소스로 하여 즉시 푸시합니다.
gh repo create my_project --public --source=. --push
--public: 리포지토리를 공개로 설정합니다. (비공개를 원하면 --private 사용)

--source=.: 현재 디렉터리(.)를 소스로 지정합니다.

--push: 생성 즉시 로컬 main (또는 master) 브랜치를 GitHub로 푸시합니다.

이제 GitHub 계정에 my_project 리포지토리가 생성되었고, .venv 폴더를 제외한 모든 파일이 업로드되었습니다.