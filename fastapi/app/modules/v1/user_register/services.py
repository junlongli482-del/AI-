from sqlalchemy.orm import Session
import hashlib
import secrets
from .models import User
from .schemas import UserRegisterRequest


class UserRegisterService:

    @staticmethod
    def hash_password(password: str) -> str:
        """使用SHA256+盐值加密密码"""
        # 生成随机盐值
        salt = secrets.token_hex(16)
        # 密码+盐值进行SHA256加密
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        # 返回 盐值:哈希值 的格式
        return f"{salt}:{password_hash}"

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """验证密码"""
        try:
            salt, hash_value = hashed_password.split(':')
            return hashlib.sha256((password + salt).encode()).hexdigest() == hash_value
        except:
            return False

    @staticmethod
    def check_username_exists(db: Session, username: str) -> bool:
        """检查用户名是否已存在"""
        return db.query(User).filter(User.username == username).first() is not None

    @staticmethod
    def check_email_exists(db: Session, email: str) -> bool:
        """检查邮箱是否已存在"""
        return db.query(User).filter(User.email == email).first() is not None

    @staticmethod
    def create_user(db: Session, user_data: UserRegisterRequest) -> User:
        """创建新用户"""
        # 加密密码
        hashed_password = UserRegisterService.hash_password(user_data.password)

        # 创建用户对象
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password
        )

        # 保存到数据库
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user