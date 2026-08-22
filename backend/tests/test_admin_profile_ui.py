import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import create_app
from models import db, Admin

def test_admin_profile_and_auth():
    app = create_app("test")
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        db.create_all()
        # Seed admin
        admin = Admin.query.filter_by(username="admin").first()
        if not admin:
            admin = Admin(username="admin", email="admin@zeal.edu.in")
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()

        client = app.test_client()

        # 1. Test Admin Login
        login_res = client.post("/api/login", json={"username": "admin", "password": "admin123"})
        assert login_res.status_code == 200, f"Login failed: {login_res.data}"
        login_data = login_res.get_json()
        assert "user" in login_data
        assert login_data["user"]["role"] == "Administrator"
        assert login_data["user"]["avatar"] == "/images/admin-avatar.svg"
        print("[OK] Admin login returned user role and avatar info.")

        # 2. Test Check Auth
        auth_res = client.get("/api/check-auth")
        assert auth_res.status_code == 200
        auth_data = auth_res.get_json()
        assert auth_data["authenticated"] is True
        assert auth_data["user_type"] == "admin"
        assert auth_data["username"] == "admin"
        assert auth_data["role"] == "Administrator"
        assert auth_data["avatar"] == "/images/admin-avatar.svg"
        print("[OK] /api/check-auth returned authenticated admin profile info.")

        # 3. Test Static SVG Avatar Delivery
        avatar_res = client.get("/images/admin-avatar.svg")
        assert avatar_res.status_code == 200
        assert b"<svg" in avatar_res.data
        print("[OK] /images/admin-avatar.svg served successfully.")

        # 4. Test Index Page & View Page serving
        index_res = client.get("/")
        assert index_res.status_code == 200
        assert b"app-header-admin" in index_res.data
        assert b"View Records" not in index_res.data
        assert b"formAdminAvatar" in index_res.data
        print("[OK] Admission Form page header updated and 'View Records' confirmed removed.")

        # 5. Test Admin Logout
        logout_res = client.post("/api/logout")
        assert logout_res.status_code == 200
        check_logged_out = client.get("/api/check-auth")
        assert check_logged_out.status_code == 401
        print("[OK] Admin logout works cleanly.")

if __name__ == "__main__":
    test_admin_profile_and_auth()
    print("\nALL ADMIN PROFILE & ADMISSION HEADER TESTS PASSED!")
