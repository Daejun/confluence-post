#!/usr/bin/env bash
# PlantUML 로컬 문법 검사 환경을 갖춘다.
# 사내 Confluence 서버와 같은 버전의 jar 을 받아, 게시 전에 문법 오류를 잡는다.
# 여러 번 돌려도 안전하다.
set -u

VERSION="${PLANTUML_VERSION:-1.2024.8}"
DEST="${PLANTUML_JAR:-$HOME/.local/share/plantuml/plantuml.jar}"
URL="https://github.com/plantuml/plantuml/releases/download/v${VERSION}/plantuml-${VERSION}.jar"

say() { printf '%s\n' "$*"; }
missing=0

# 1. java
if command -v java >/dev/null 2>&1; then
  say "java: $(java -version 2>&1 | head -1)"
else
  say "java: 없음"
  say "  설치가 필요하고 root 권한이 있어야 한다. 직접 실행해 주세요:"
  say "    sudo apt install -y default-jre-headless    # Debian/Ubuntu"
  say "    sudo dnf install -y java-latest-openjdk-headless   # Fedora/RHEL"
  missing=1
fi

# 2. graphviz — sequence/mindmap 말고는 dot 이 있어야 그려진다
if command -v dot >/dev/null 2>&1; then
  say "graphviz: $(dot -V 2>&1 | head -1)"
else
  say "graphviz: 없음 (sequence·mindmap 외 다이어그램의 로컬 검사가 실패한다)"
  say "    sudo apt install -y graphviz"
  say "    sudo dnf install -y graphviz"
fi

# 3. plantuml jar
if [ -f "$DEST" ] && java -jar "$DEST" -version 2>/dev/null | grep -q "$VERSION"; then
  say "plantuml.jar: 이미 $VERSION ($DEST)"
else
  say "plantuml.jar: $VERSION 내려받는다"
  say "  $URL"
  mkdir -p "$(dirname "$DEST")" || exit 1
  tmp="$DEST.part"
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL --retry 3 -o "$tmp" "$URL" || { say "  내려받기 실패"; exit 1; }
  elif command -v wget >/dev/null 2>&1; then
    wget -q -O "$tmp" "$URL" || { say "  내려받기 실패"; exit 1; }
  else
    say "  curl 도 wget 도 없다"; exit 1
  fi
  # 받은 것이 정말 그 버전의 jar 인지 실행해서 확인한다
  if [ "$missing" = 0 ] && ! java -jar "$tmp" -version 2>/dev/null | grep -q "$VERSION"; then
    say "  받은 파일이 $VERSION 이 아니다. 버린다"
    rm -f "$tmp"; exit 1
  fi
  mv "$tmp" "$DEST"
  say "plantuml.jar: $DEST"
fi

# 4. 실제로 도는지 본다
if [ "$missing" = 0 ] && [ -f "$DEST" ]; then
  say ""
  say "버전: $(java -jar "$DEST" -version 2>/dev/null | head -1)"
  say "dot:  $(java -jar "$DEST" -testdot 2>&1 | head -1)"
  if printf '@startuml\nA -> B: ok\n@enduml\n' | java -jar "$DEST" -checkonly -pipe >/dev/null 2>&1; then
    say "문법 검사: 동작"
  else
    say "문법 검사: 동작 안 함"
  fi
fi

say ""
if [ "$missing" = 0 ] && [ -f "$DEST" ]; then
  say "준비됐다. check.py 가 이제 plantuml 본문의 문법을 실제로 검사한다."
else
  say "위의 설치를 마친 뒤 이 스크립트를 다시 돌린다."
fi
