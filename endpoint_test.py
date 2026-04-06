import requests

BASE_URL = 'http://127.0.0.1:5000'

def test_endpoints():
    session = requests.Session()
    
    # 1. Test Registration with long username
    long_username = "A_very_long_username_" + "x" * 150
    print(f"Testing registration with username length: {len(long_username)}")
    
    reg_data = {
        'username': long_username,
        'email': 'test_ai@example.com',
        'password': 'password123'
    }
    
    r = session.post(f"{BASE_URL}/register", data=reg_data, allow_redirects=True)
    if "Your account has been created" in r.text or "Email or Username already exists" in r.text:
        print("[OK] Registration endpoint passed (or user already exists)")
    else:
        print("[FAIL] Registration endpoint FAILED")
        # print(r.text[:500])
        return

    # 2. Test Login
    login_data = {
        'email': 'test_ai@example.com',
        'password': 'password123'
    }
    r = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=True)
    if "Welcome" in r.text or "Logout" in r.text or "Major Advisor" in r.text:
        print("[OK] Login endpoint passed")
    else:
        print("[FAIL] Login endpoint FAILED")
        return

    # 3. Test Recommendation (Predict)
    predict_data = {
        'math': 'A', 'english': 'B', 'kiswahili': 'B',
        'biology': 'C', 'physics': 'B+', 'chemistry': 'B-',
        'humanities': 'A', 'tech_bus': 'A',
        'interest': 'I want to be a digital marketing manager or CEO of a startup.'
    }
    print("Testing recommendation with interest: 'I want to be a digital marketing manager'")
    r = session.post(f"{BASE_URL}/predict", data=predict_data, allow_redirects=True)
    
    if r.status_code == 200:
        print("[OK] Predict endpoint returned 200")
        # Check for AI reasoning
        if "Based on your description" not in r.text and ("manager" in r.text.lower() or "startup" in r.text.lower()):
            print("[OK] AI Reasoning is dynamic and personalized!")
        elif "Based on your description" in r.text:
            print("(!) Warning: Still seeing hardcoded 'Based on your description' prefix.")
        else:
            print("[FAIL] Could not verify unique AI reasoning in response.")
            # print(r.text)
    # 4. Test Admin Dashboard
    r = session.get(f"{BASE_URL}/admin", allow_redirects=True)
    if "Admin Dashboard" in r.text and "Manage Users" in r.text:
        print("[OK] Admin Dashboard endpoint passed")
    else:
        print("[FAIL] Admin Dashboard access FAILED (is_admin check failed?)")
        return

    # 5. Test Delete User Confirmation Page
    # Find the user ID from the admin page
    # Since it's a fresh DB, the test user might be ID 1
    r = session.get(f"{BASE_URL}/admin/delete-user/1", allow_redirects=True)
    if "Are you sure you want to delete user" in r.text:
        print("[OK] Admin Delete Confirmation endpoint passed")
    else:
        print("[FAIL] Admin Delete Confirmation FAILED")
        # print(r.text)

if __name__ == "__main__":
    try:
        test_endpoints()
    except Exception as e:
        print(f"Test crashed: {e}")
