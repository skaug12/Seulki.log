# HFK 상품 관리 에이전트

상품 백업 → 완성도 평가 → 보완 → 동기화까지 상품 관리 전체 워크플로우를 실행합니다.

## 사용법

```
/run-product-ops
```

## 실행 워크플로우

### Step 1: 상품 백업 (backup-products)

1. 대상 카테고리 선택
2. MCP Imweb `imweb_get_products`로 아임웹 상품 조회
3. 각 상품의 상세 정보를 `imweb_get_product`로 가져오기
4. HTML → Markdown 변환하여 Obsidian 노트로 저장

**사용자 확인**: 백업 결과 확인

### Step 2: 완성도 평가 (evaluate-notes)

1. 백업된 카테고리의 모든 노트를 평가 기준에 따라 점수 매기기
2. 결과를 테이블로 출력
3. 긴급 이슈를 MCP Apple Reminders `bulk_create`로 미리알림 등록

**사용자 확인**: 평가 결과와 수정 대상 확인

### Step 3: 보완 제안 [선택]

70점 미만 노트에 대해:
- 부족한 섹션 자동 식별
- 보완 내용 제안 (expand-idea 스킬 활용)
- 사용자 승인 후 노트에 반영
- `status: draft`로 변경

### Step 4: 아임웹 동기화 (sync-products) [선택]

수정된 노트가 있으면:
1. `status: draft` 파일 목록 보여주기
2. MCP Imweb 도구로 동기화
3. `status: synced`로 변경

## 완료 요약

- 백업된 상품 수
- 평가 결과 (평균 점수, 최저/최고)
- 등록된 미리알림 수
- 보완/동기화된 노트 수
