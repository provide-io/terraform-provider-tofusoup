# Lint Fix Plan: terraform-provider-tofusoup

**Total Violations:** 16
**Generated:** 2025-11-16
**Priority:** MEDIUM (Terraform provider)

---

## Violation Summary

| Code | Count | Description | Auto-fixable |
|------|-------|-------------|--------------|
| B017 | 10 | Blind exception assertions | Manual |
| C901 | 3 | Function too complex (>10) | Manual |
| SIM108 | 2 | Use ternary operator | Yes (unsafe) |
| RUF043 | 1 | Regex pattern metacharacter | Manual |

---

## Files Requiring Fixes

### Source Code (3 violations)
- `src/tofusoup/tf/components/data_sources/state_info.py` - C901
- `src/tofusoup/tf/components/data_sources/state_outputs.py` - C901, SIM108
- `src/tofusoup/tf/components/data_sources/state_resources.py` - C901, SIM108

### Tests (13 violations)
- `tests/data_sources/test_module_search/test_basic.py` - B017
- `tests/data_sources/test_module_versions.py` - B017
- `tests/data_sources/test_registry_search/test_basic.py` - B017
- `tests/data_sources/test_state_info_errors.py` - B017, RUF043
- `tests/data_sources/test_state_info_schema.py` - B017
- `tests/data_sources/test_state_outputs/test_basic.py` - B017
- `tests/data_sources/test_state_resources.py` - B017

---

## Fix Strategy by Category

### Phase 1: Quick Wins (Auto-fixable)

**Estimated time:** 5 minutes

```bash
cd /Users/tim/code/gh/provide-io/terraform-provider-tofusoup
ruff check --fix .
ruff check --fix --unsafe-fixes .
```

Auto-fixes:
- SIM108 (2) - Ternary operators in state data sources

**Expected reduction:** 2 violations (12%)

**Example fix:**
```python
# BEFORE
if isinstance(output_type, list):
    type_str = json.dumps(output_type)
else:
    type_str = str(output_type)

# AFTER
type_str = json.dumps(output_type) if isinstance(output_type, list) else str(output_type)
```

---

### Phase 2: Blind Exception Assertions (B017)

**Location:** tests/
**Estimated time:** 30 minutes
**10 violations**

All in test files testing frozen/immutable objects:

```python
# BEFORE - Too broad
with pytest.raises(Exception):
    config.state_path = "/other/path"  # type: ignore

# AFTER - Specific exception for frozen attrs
import attrs.exceptions
with pytest.raises(attrs.exceptions.FrozenInstanceError):
    config.state_path = "/other/path"  # type: ignore

# OR if using dataclass
with pytest.raises(dataclasses.FrozenInstanceError):
    config.field = "value"

# OR generic for various frozen implementations
with pytest.raises((AttributeError, TypeError)):
    config.field = "value"
```

**Pattern in tests:**
- Testing that Config instances are frozen/immutable
- Testing that State instances are frozen/immutable
- Each needs specific exception class instead of generic `Exception`

---

### Phase 3: Complex Functions (C901)

**Location:** State data source read() methods
**Estimated time:** 1-2 hours
**3 violations**

**Complex functions:**
1. `state_info.py:153` - `read()` complexity 12 (threshold 10)
2. `state_outputs.py:150` - `read()` complexity 12
3. `state_resources.py:174` - `read()` complexity 15

**Refactoring pattern:**
```python
# BEFORE - Single large read() method
async def read(self, ctx: ResourceContext) -> StateInfoState:
    if not ctx.config:
        raise ValueError("...")
    # 50+ lines of parsing, validation, error handling
    pass

# AFTER - Extract helper methods
async def _validate_config(self, ctx: ResourceContext) -> StateInfoConfig:
    if not ctx.config:
        raise ValueError("...")
    return ctx.config

async def _parse_state_file(self, path: Path) -> dict:
    # State file parsing logic
    pass

async def _build_state(self, raw_data: dict) -> StateInfoState:
    # State object construction
    pass

async def read(self, ctx: ResourceContext) -> StateInfoState:
    config = await self._validate_config(ctx)
    raw_data = await self._parse_state_file(config.state_path)
    return await self._build_state(raw_data)
```

---

### Phase 4: Regex Pattern (RUF043)

**Location:** `tests/data_sources/test_state_info_errors.py`
**Estimated time:** 5 minutes

```python
# BEFORE - Metacharacters not escaped
match="pattern with . or * or other regex chars"

# AFTER - Use raw string or escape
match=r"pattern with \. or \* or other regex chars"
```

---

## Recommended Execution Order

1. **Run auto-fix** - SIM108 ternary operators
2. **Fix B017 blind exceptions** - Improve test quality
3. **Fix RUF043 regex pattern** - Quick fix
4. **Refactor C901** - Optional, time-intensive

---

## Commands

```bash
# Check current state
cd /Users/tim/code/gh/provide-io/terraform-provider-tofusoup
ruff check . 2>&1 | tail -10

# Auto-fix
ruff check --fix .
ruff check --fix --unsafe-fixes .

# Format
ruff format .

# Run tests after B017 fixes
uv run pytest tests/

# Type check
mypy src/

# Verify
ruff check . 2>&1 | grep "Found"
```

---

## Alternative: Relax Rules

```toml
[tool.ruff.lint]
ignore = [
    "C901",  # Complex read() methods are acceptable
]

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["B017", "RUF043"]  # Test-specific patterns
```

---

## Success Criteria

- [ ] All SIM108 ternary operators applied
- [ ] All B017 blind exceptions replaced with specific types
- [ ] Regex pattern properly escaped
- [ ] Complex functions refactored or documented
- [ ] Total violations: 0 or documented exceptions
