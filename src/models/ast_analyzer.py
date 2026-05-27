"""
ast_analyzer.py: AST 기반 코드 복잡도 정적 분석
"""

import ast
from radon.complexity import cc_visit
from .data_models import ASTResult, ClapComponents


# ──────────────────────────────────────────────
# 상수 정의
# ──────────────────────────────────────────────

CLAP_WEIGHTS = {
    "branch": 1.0,
    "loop":   1.2,
    "depth":  1.5,
    "func":   0.5,
}

MCCABE_LABELS = {
    "simple":  (0,  10,  "단순"),
    "middle":  (11, 20,  "중간"),
    "complex": (21, 999, "복잡"),
}

NESTING_NODES = (
    ast.If, ast.For, ast.While,
    ast.With, ast.Try, ast.FunctionDef
)


# ──────────────────────────────────────────────
# ASTAnalyzer
# ──────────────────────────────────────────────

class ASTAnalyzer:

    def analyze(self, file_path: str) -> ASTResult:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()
        except Exception as e:
            return ASTResult(
                file_path=file_path,
                valid=False,
                feedback_message=f"파일 읽기 실패: {e}"
            )

        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            return ASTResult(
                file_path=file_path,
                valid=False,
                feedback_message=f"문법 오류로 분석 불가: {e}"
            )

        line_count = len(source.splitlines())
        function_count = sum(1 for _ in ast.walk(tree) if isinstance(_, ast.FunctionDef))
        clap_components = self._compute_clap_score(tree)
        mccabe_score, mccabe_label = self._compute_mccabe(source)
        feedback_message = self._build_feedback(clap_components, mccabe_score)

        return ASTResult(
            file_path=file_path,
            valid=True,
            line_count=line_count,
            function_count=function_count,
            clap_components=clap_components,
            mccabe_score=mccabe_score,
            mccabe_label=mccabe_label,
            feedback_message=feedback_message
        )

    # ──────────────────────────────────────────────
    # McCabe 순환 복잡도
    # ──────────────────────────────────────────────

    def _compute_mccabe(self, source: str) -> tuple[float, str]:
        try:
            results = cc_visit(source)
            if not results:
                return 0.0, "단순"
            score = max(block.complexity for block in results)
        except Exception:
            return 0.0, "단순"

        for _, (lo, hi, label) in MCCABE_LABELS.items():
            if lo <= score <= hi:
                return float(score), label

        return float(score), "복잡"

    # ──────────────────────────────────────────────
    # CLAP 복잡도 공식
    # ──────────────────────────────────────────────

    def _compute_clap_score(self, tree: ast.AST) -> ClapComponents:
        branch_count = 0
        loop_count = 0
        func_lengths = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.IfExp)):
                branch_count += 1
            elif isinstance(node, (ast.For, ast.While)):
                loop_count += 1
            elif isinstance(node, ast.FunctionDef):
                if hasattr(node, "end_lineno") and hasattr(node, "lineno"):
                    func_lengths.append(node.end_lineno - node.lineno + 1)

        nesting_depth = self._max_nesting_depth(tree)
        function_length = sum(func_lengths) / len(func_lengths) if func_lengths else 0.0

        score = (
            branch_count     * CLAP_WEIGHTS["branch"] +
            loop_count       * CLAP_WEIGHTS["loop"]   +
            nesting_depth    * CLAP_WEIGHTS["depth"]  +
            function_length  * CLAP_WEIGHTS["func"]
        )

        return ClapComponents(
            branch_count=branch_count,
            loop_count=loop_count,
            nesting_depth=nesting_depth,
            function_length=round(function_length, 2),
            score=round(score, 2)
        )

    # ──────────────────────────────────────────────
    # 최대 중첩 깊이 계산
    # ──────────────────────────────────────────────

    def _max_nesting_depth(self, tree: ast.AST) -> int:
        def _dfs(node: ast.AST, depth: int) -> int:
            current = depth + 1 if isinstance(node, NESTING_NODES) else depth
            max_depth = current
            for child in ast.iter_child_nodes(node):
                max_depth = max(max_depth, _dfs(child, current))
            return max_depth

        return _dfs(tree, 0)

    # ──────────────────────────────────────────────
    # 피드백 메시지 생성
    # ──────────────────────────────────────────────

    def _build_feedback(self, cc: ClapComponents, mccabe_score: float) -> str:
        messages = []

        if cc.nesting_depth >= 3:
            messages.append("중첩 깊이가 높아 코드 가독성이 낮습니다.")
        if cc.function_length > 20:
            messages.append("함수 분리를 권장합니다.")
        if cc.loop_count >= 3:
            messages.append("반복문 사용 빈도가 높습니다.")
        if cc.branch_count >= 5:
            messages.append("조건문이 과도하게 중첩되어 있습니다.")
        if mccabe_score >= 21:
            messages.append("McCabe 복잡도가 높습니다. 리팩토링을 권장합니다.")

        if not messages:
            messages.append("코드 구조가 양호합니다.")

        return " ".join(messages)