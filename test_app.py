#!/usr/bin/env python3
"""
Test script for the Notion-IMDB Movie List Update application.
This script tests the application with mock data to ensure all components work correctly.
"""

import sys
sys.path.insert(0, 'src')

from unittest.mock import Mock, patch, MagicMock
from imdbinfo import models

def test_basic_functionality():
    """Test basic application functionality with mocked dependencies."""
    print("=" * 70)
    print("Testing Notion-IMDB Movie List Update Application")
    print("=" * 70)
    
    import main
    
    # Mock configuration
    with patch('main.config.NOTION_TOKEN', 'test-token'), \
         patch('main.config.NOTION_DATABASE_URL', 'https://notion.so/test/abc123def456'):
        
        # Create mock Notion API
        mock_notion_api = Mock()
        mock_notion_api.get_database_id_from_url.return_value = 'test-db-id'
        
        # Create mock pages from Notion
        mock_pages = [
            {
                "id": "page-1",
                "properties": {
                    "Title": {
                        "title": [{"text": {"content": "The Shawshank Redemption"}}]
                    },
                    "IMDB": {
                        "url": None
                    }
                }
            },
            {
                "id": "page-2",
                "properties": {
                    "Title": {
                        "title": []
                    },
                    "IMDB": {
                        "url": "https://www.imdb.com/title/tt0133093/"
                    }
                }
            },
            {
                "id": "page-3",
                "properties": {
                    "Title": {
                        "title": [{"text": {"content": "Game of Thrones"}}]
                    },
                    "IMDB": {
                        "url": "https://www.imdb.com/title/tt0944947/"
                    }
                }
            }
        ]
        mock_notion_api.get_empty_pages.return_value = mock_pages
        
        # Create mock IMDB adapter
        mock_imdb_adapter = Mock()
        
        # Mock movie for search by title
        mock_movie1 = Mock(
            title="The Shawshank Redemption",
            imdb_id="0111161",
            is_series=False,
            director="Frank Darabont",
            duration=142,
            rating=9.3,
            plot="Two imprisoned men bond over a number of years, finding solace and eventual redemption.",
            genres=["Drama"]
        )
        mock_imdb_adapter.search_movie.return_value = mock_movie1
        
        # Mock movies for get by ID
        def get_movie_by_id(movie_id):
            if movie_id == "0133093":
                return Mock(
                    title="The Matrix",
                    imdb_id="0133093",
                    is_series=False,
                    director="Wachowskis",
                    duration=136,
                    rating=8.7,
                    plot="A computer hacker discovers the truth about reality.",
                    genres=["Action", "Sci-Fi"]
                )
            elif movie_id == "0944947":
                return Mock(
                    title="Game of Thrones",
                    imdb_id="0944947",
                    is_series=True,
                    director=None,
                    duration=57,
                    rating=9.2,
                    plot="Nine noble families fight for control over the lands of Westeros.",
                    genres=["Action", "Adventure", "Drama"]
                )
            return None
        
        mock_imdb_adapter.get_movie.side_effect = get_movie_by_id
        
        # Patch the classes
        with patch('main.NotionAPI', return_value=mock_notion_api), \
             patch('main.IMDbInfoAdapter', return_value=mock_imdb_adapter):
            
            print("\n[1] Running main() function...")
            try:
                main.main()
                print("    ✓ Execution completed successfully\n")
            except Exception as e:
                print(f"    ✗ Error: {e}\n")
                import traceback
                traceback.print_exc()
                return False
            
            # Verify the right methods were called
            print("[2] Verifying Notion API calls...")
            if mock_notion_api.get_database_id_from_url.called:
                print("    ✓ get_database_id_from_url called")
            else:
                print("    ✗ get_database_id_from_url not called")
                return False
            
            if mock_notion_api.get_empty_pages.called:
                print("    ✓ get_empty_pages called")
            else:
                print("    ✗ get_empty_pages not called")
                return False
            
            print("\n[3] Verifying IMDB adapter calls...")
            if mock_imdb_adapter.search_movie.called:
                print(f"    ✓ search_movie called")
            else:
                print("    ✗ search_movie not called")
            
            if mock_imdb_adapter.get_movie.called:
                print(f"    ✓ get_movie called")
            else:
                print("    ✗ get_movie not called")
            
            print("\n[4] Verifying Notion page updates...")
            call_count = mock_notion_api.update_page.call_count
            expected_updates = 3
            if call_count == expected_updates:
                print(f"    ✓ update_page called {call_count} times (expected: {expected_updates})")
            else:
                print(f"    ✗ update_page called {call_count} times (expected: {expected_updates})")
                return False
            
            # Verify the properties of updates
            print("\n[5] Verifying update properties...")
            for i, call in enumerate(mock_notion_api.update_page.call_args_list, 1):
                page_id, properties = call[0]
                title = properties.get('Title', {}).get('title', [{}])[0].get('text', {}).get('content', 'N/A')
                imdb_url = properties.get('IMDB', {}).get('url', 'N/A')
                print(f"    Update {i}:")
                print(f"      - Title: {title}")
                print(f"      - IMDB URL: {imdb_url}")
                
                # Verify URL format
                if imdb_url.startswith('https://www.imdb.com/title/tt') and 'tttt' not in imdb_url:
                    print(f"      ✓ URL format is correct")
                else:
                    print(f"      ✗ URL format is incorrect")
                    return False
    
    print("\n" + "=" * 70)
    print("✓ All tests passed successfully!")
    print("=" * 70)
    return True

def test_error_scenarios():
    """Test error handling scenarios."""
    print("\n" + "=" * 70)
    print("Testing Error Handling")
    print("=" * 70)
    
    from exceptions import MovieNotFound
    import main
    
    # Test MovieNotFound handling
    print("\n[1] Testing MovieNotFound handling...")
    with patch('main.config.NOTION_TOKEN', 'test-token'), \
         patch('main.config.NOTION_DATABASE_URL', 'https://notion.so/test/abc123'):
        
        mock_notion_api = Mock()
        mock_notion_api.get_database_id_from_url.return_value = 'test-db-id'
        mock_notion_api.get_empty_pages.return_value = [
            {
                "id": "page-1",
                "properties": {
                    "Title": {"title": [{"text": {"content": "Nonexistent Movie"}}]},
                    "IMDB": {"url": None}
                }
            }
        ]
        
        mock_imdb_adapter = Mock()
        mock_imdb_adapter.search_movie.side_effect = MovieNotFound("Movie not found")
        
        with patch('main.NotionAPI', return_value=mock_notion_api), \
             patch('main.IMDbInfoAdapter', return_value=mock_imdb_adapter):
            
            try:
                main.main()
                if not mock_notion_api.update_page.called:
                    print("    ✓ Page not updated when movie not found")
                else:
                    print("    ✗ Page was incorrectly updated")
                    return False
            except Exception as e:
                print(f"    ✗ Unexpected exception: {e}")
                return False
    
    print("\n" + "=" * 70)
    print("✓ Error handling tests passed!")
    print("=" * 70)
    return True

if __name__ == "__main__":
    print("\n")
    success = test_basic_functionality()
    if success:
        success = test_error_scenarios()
    
    if success:
        print("\n🎉 All tests completed successfully!\n")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!\n")
        sys.exit(1)
