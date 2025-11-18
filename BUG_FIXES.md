# Bug Fixes and Improvements

## Summary

This document outlines the bugs found and fixed in the Notion-IMDB Movie List Update application.

## Bugs Fixed

### 1. Critical: Database ID Format - Missing UUID Hyphens

**Location:** `src/notion_api.py` lines 84-94

**Issue:**
The Notion API requires database IDs in UUID format with hyphens (e.g., `de18023b-1590-4f87-af9b-47aea99feeaa`), but the code was extracting IDs from URLs without hyphens (e.g., `de18023b15904f87af9b47aea99feeaa`).

**Error Message:**
```
Could not find database with ID: de18023b-1590-4f87-af9b-47aea99feeaa. 
Make sure the relevant pages and databases are shared with your integration.
```

**Root Cause:**
```python
# Old code - extracts ID without hyphens
result = re.search(r"notion\.so/[^/]+/(\w+)", database_url)
if result:
    result = result.group(1)
    if len(result) == 32:
        return result  # Returns: de18023b15904f87af9b47aea99feeaa
```

**Fix:**
Converts the extracted ID to proper UUID format with hyphens:
```python
# New code - converts to UUID format
result = re.search(r"notion\.so/[^/]+/([\w-]+)", database_url)
if result:
    database_id = result.group(1)
    id_without_hyphens = database_id.replace("-", "")
    if len(id_without_hyphens) == 32:
        # Convert to UUID format (8-4-4-4-12)
        return f"{id_without_hyphens[0:8]}-{id_without_hyphens[8:12]}-{id_without_hyphens[12:16]}-{id_without_hyphens[16:20]}-{id_without_hyphens[20:32]}"
```

**Benefits:**
- Handles URLs with or without hyphens in the ID
- Ensures proper UUID format for Notion API
- Returns: `de18023b-1590-4f87-af9b-47aea99feeaa`

**Impact:** 
- **High** - The Notion API cannot find databases without proper UUID formatting
- This was causing the "Could not find database" error even when the database existed and was shared

### 2. Critical: AttributeError when search_title returns None

**Location:** `src/imdbinfo_adapter.py` line 21

**Issue:**
The `search_title()` function from the imdbinfo library can return `None` when no search results are found. The code was attempting to access the `.titles` attribute on a `None` object, causing an `AttributeError`.

**Root Cause:**
```python
search_results = search_title(title)
if not search_results.titles:  # ❌ Crashes if search_results is None
    raise MovieNotFound(...)
```

**Fix:**
Added a null check before accessing the `.titles` attribute:
```python
search_results = search_title(title)
if not search_results or not search_results.titles:  # ✅ Safe
    raise MovieNotFound(...)
```

**Impact:** 
- **High** - This would cause the application to crash whenever a movie search returned no results
- This is one of the reasons the app "stopped working"

### 3. Critical: Notion API Breaking Change - databases.query() removed

**Location:** `src/notion_api.py` line 67

**Issue:**
The Notion SDK (notion-client) version 2.7.0 introduced a breaking change where `databases.query()` was removed. The API now uses `data_sources.query()` instead, as databases are now treated as "data sources" in the Notion API.

**Error Message:**
```
'DatabasesEndpoint' object has no attribute 'query'
```

**Root Cause:**
```python
# Old API (no longer works in notion-client >= 2.7.0)
return self.client.databases.query(database_id=database_id, **empty_page_filter).get("results")
```

**Fix:**
Updated to use the new data sources endpoint:
```python
# New API (notion-client >= 2.7.0)
return self.client.data_sources.query(data_source_id=database_id, **empty_page_filter).get("results")
```

**Changes Required:**
- Changed endpoint: `client.databases.query` → `client.data_sources.query`
- Changed parameter name: `database_id=` → `data_source_id=`

**Impact:**
- **High** - This would cause the application to crash immediately when trying to query the Notion database
- This is the **primary reason** the app stopped working for users with notion-client >= 2.7.0

### 4. Improvement: IMDB ID Format Safety Check

**Location:** `src/updater.py` line 47

**Issue:**
The IMDB URL generation assumed the `imdb_id` field never includes the "tt" prefix. However, depending on how the imdbinfo library returns data, this could lead to double-prefixing (e.g., `https://www.imdb.com/title/tttt0111161`).

**Original Code:**
```python
"IMDB": {"url": f"https://www.imdb.com/title/tt{movie.imdb_id}"}
```

**Fix:**
Added a check to handle both prefixed and non-prefixed IDs:
```python
# Ensure imdb_id has the 'tt' prefix for the URL
imdb_id = movie.imdb_id if movie.imdb_id.startswith('tt') else f"tt{movie.imdb_id}"
properties = {
    ...
    "IMDB": {"url": f"https://www.imdb.com/title/{imdb_id}"},
}
```

**Impact:**
- **Medium** - Prevents potential malformed URLs if the library's return format changes
- Makes the code more robust and defensive

## Testing

A comprehensive test suite has been created in `test_app.py` that validates:

1. ✅ Basic application flow with mocked dependencies
2. ✅ Search by movie title
3. ✅ Fetch by IMDB URL
4. ✅ TV series handling
5. ✅ Error handling for missing movies
6. ✅ Error handling for Notion API errors
7. ✅ IMDB URL format correctness
8. ✅ Edge cases (empty titles, None URLs, etc.)

## Running Tests

```bash
python test_app.py
```

All tests pass successfully with the current fixes.

## Root Cause Analysis

The application stopped working because of **two critical bugs**:

1. **Notion API Breaking Change (Primary Cause):**
   - notion-client library version 2.7.0 removed `databases.query()` method
   - Changed to `data_sources.query()` with different parameter names
   - This caused an immediate AttributeError when trying to query databases

2. **Search Result Null Handling (Secondary Cause):**
   - The imdbinfo library can return `None` when searches fail
   - IMDB website structure changes could affect the library's scraping
   - Rate limiting or blocking could cause search failures
   - Network issues could lead to None returns

3. **Contributing Factors:**
   - No version pinning in requirements.txt allowed automatic updates to breaking versions
   - No unit tests to catch these issues before deployment

## Recommendations

1. ✅ **Already Implemented:** Add null checks for all external API responses
2. ✅ **Already Implemented:** Defensive programming for URL/ID formatting
3. ✅ **Already Implemented:** Update to new Notion API (data_sources.query)
4. 🔄 **Future:** Pin dependency versions to avoid breaking changes
5. 🔄 **Future:** Add retry logic for network failures
6. 🔄 **Future:** Add logging for all API responses to aid debugging
7. 🔄 **Future:** Consider caching IMDB data to reduce API calls
8. 🔄 **Future:** Add integration tests that can run against a test Notion database
9. 🔄 **Future:** Set up CI/CD to run tests before deployment

## Compatibility

- ✅ Python 3.12+ (tested)
- ✅ imdbinfo 0.6.3 (current version)
- ✅ notion-client 2.7.0 (current version) - **Now compatible!**
- ✅ All dependencies install and work correctly
