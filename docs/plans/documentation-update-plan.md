# Documentation Update Plan: Rename vs Update Approach

**Created:** July 7, 2025  
**Status:** ✅ COMPLETED  
**Issue:** Documentation references are inconsistent between `app.py` (legacy) and `app_mlx_api.py` (current)

## ✅ IMPLEMENTATION COMPLETED

**Files renamed:**
- `app_mlx_api.py` → `app.py` (now the main application)
- `app.py` → `app_legacy.py` (legacy version preserved)

**Files updated:**
- ✅ `launch.sh` - Updated to use `app.py`
- ✅ `docs/deployment-guide.md` - Updated references to `app.py`
- ✅ `README.md` - Updated file structure section
- ✅ `docs/implementation-guide.md` - Added architecture evolution note

**Backup files created:**
- `app_original_backup.py` (backup of original app.py)
- `app_mlx_api_backup.py` (backup of original app_mlx_api.py)

## Two Potential Solutions

### Option A: Rename Files (RECOMMENDED)
Rename `app_mlx_api.py` → `app.py` and `app.py` → `app_legacy.py`

### Option B: Update All Documentation
Keep current filenames and update all documentation references

## Analysis: Why Renaming is Better

### Current State Assessment

**Files that expect `app.py` as main:**
- `Dockerfile` (line 34: `ENV FLASK_APP=app.py`, line 39: `CMD ["python", "app.py"]`)
- `docs/implementation-guide.md` (multiple references)
- `docs/implementation-options.md` (original planning document)
- Flask/Python conventions

**Files that currently reference `app_mlx_api.py`:**
- `launch.sh` (line 61: `python app_mlx_api.py &`)
- `docs/deployment-guide.md` (2 references)
- `README.md` (correctly identifies current vs legacy)

**Historical Context:**
- `implementation-options.md` was the **original planning document** that designed the app around `app.py`
- The MLX API approach was an evolution that led to creating `app_mlx_api.py`
- Most documentation was written expecting `app.py` as the main file

### Benefits of Renaming Approach

#### 1. **Minimal Changes Required**
- Only 3 files need updates: `launch.sh`, `docs/deployment-guide.md`, `README.md`
- vs. updating 6+ files and multiple references throughout

#### 2. **Follows Conventions**
- Flask apps typically use `app.py` as the main entry point
- Docker expects `app.py` (already configured)
- Python packaging conventions expect main module as `app.py`

#### 3. **Respects Original Design**
- `implementation-options.md` was the blueprint - it planned for `app.py`
- Current situation is an artifact of iterative development
- Renaming aligns reality with original intent

#### 4. **Cleaner Architecture**
- Main app = `app.py` (clear, conventional)
- Legacy app = `app_legacy.py` (clearly marked as old)
- No ambiguity about which is current

#### 5. **Docker Compatibility**
- Dockerfile already expects `app.py`
- No container changes needed

## Proposed Renaming Plan

### Phase 1: File Operations
```bash
# Rename current files
mv app.py app_legacy.py
mv app_mlx_api.py app.py
```

### Phase 2: Update References (3 files only)

#### 2.1 Update `launch.sh`
**Change:** Line 61
```bash
# From:
python app_mlx_api.py &

# To:
python app.py &
```

#### 2.2 Update `docs/deployment-guide.md`
**Changes:** Lines 10, 48
```markdown
# From:
- **Flask Web App** (`app_mlx_api.py`) running on port 5001
python app_mlx_api.py

# To:
- **Flask Web App** (`app.py`) running on port 5001
python app.py
```

#### 2.3 Update `README.md`
**Changes:** Lines 135-136
```markdown
# From:
├── app_mlx_api.py         # Main Flask application (MLX API version)
├── app.py                 # Legacy Flask app (direct MLX integration)

# To:
├── app.py                 # Main Flask application (MLX API version)
├── app_legacy.py          # Legacy Flask app (direct MLX integration)
```

### Phase 3: Optional Documentation Enhancements

#### 3.1 Add Historical Note to `docs/implementation-guide.md`
Add a brief note explaining the evolution:
```markdown
## Architecture Evolution

The main application (`app.py`) uses the MLX API server approach. 
A legacy version (`app_legacy.py`) with direct MLX integration is 
preserved for reference and debugging purposes.
```

## Comparison: Rename vs Update All Docs

| Aspect | Rename Files | Update Documentation |
|--------|-------------|---------------------|
| **Files to change** | 3 files | 6+ files |
| **Line changes** | ~5 lines | 15+ lines |
| **Risk of errors** | Low | Medium |
| **Convention alignment** | Perfect | Poor |
| **Docker compatibility** | No changes needed | Dockerfile updates required |
| **Future confusion** | Eliminated | Ongoing |
| **Historical accuracy** | Respects original plan | Documents evolution |

## Implementation Steps (Rename Approach)

### Step 1: Backup and Rename
```bash
# Create backup
cp app.py app_original_backup.py
cp app_mlx_api.py app_mlx_api_backup.py

# Perform rename
mv app.py app_legacy.py
mv app_mlx_api.py app.py
```

### Step 2: Update Launch Script
Update `launch.sh` line 61

### Step 3: Update Documentation
- `docs/deployment-guide.md` (2 references)
- `README.md` (file structure section)

### Step 4: Test Everything
```bash
# Test launch script
./launch.sh

# Test Docker
docker build -t prompt-optimizer .
docker run -p 6000:6000 prompt-optimizer

# Test manual startup
python app.py
```

### Step 5: Cleanup
```bash
# Remove backup files after testing
rm app_original_backup.py app_mlx_api_backup.py
```

## Recommendation

**STRONGLY RECOMMEND** the rename approach because:

1. **Aligns with original design** - `implementation-options.md` planned for `app.py`
2. **Minimal disruption** - Only 3 files need changes vs 6+
3. **Follows conventions** - Flask/Python standards expect `app.py`
4. **Docker compatibility** - Already configured for `app.py`
5. **Eliminates future confusion** - Clear main vs legacy distinction

## Files to Create/Update

### Immediate (Required)
- [ ] Rename: `app_mlx_api.py` → `app.py`
- [ ] Rename: `app.py` → `app_legacy.py`
- [ ] Update: `launch.sh` (1 line)
- [ ] Update: `docs/deployment-guide.md` (2 lines)
- [ ] Update: `README.md` (2 lines)

### Optional (Enhancement)
- [ ] Add evolution note to `docs/implementation-guide.md`
- [ ] Update CHANGELOG.md to document the rename

## Risk Assessment

**Risks:** Very low
- Simple file renames with minimal reference updates
- All changes are straightforward text replacements
- Docker and conventions already expect `app.py`

**Mitigation:**
- Create backups before renaming
- Test both launch script and Docker after changes
- Verify all startup methods work correctly

## Success Criteria

- [ ] `./launch.sh` works correctly
- [ ] `python app.py` starts the main application
- [ ] Docker container builds and runs with `app.py`
- [ ] Documentation consistently references correct files
- [ ] No broken references anywhere in the project
