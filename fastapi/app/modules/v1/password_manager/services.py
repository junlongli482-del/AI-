"""
密码管理模块 - 业务逻辑服务
"""

import hashlib
import secrets
import re
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Tuple, Dict, List
from datetime import datetime

from app.core.database import get_db

class PasswordService:
    """密码管理服务类"""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        密码加密
        使用SHA256 + 随机盐值
        返回格式：盐值:哈希值
        """
        salt = secrets.token_hex(16)  # 生成32字符的随机盐值
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        验证密码
        """
        try:
            salt, stored_hash = password_hash.split(':')
            password_hash_check = hashlib.sha256((password + salt).encode()).hexdigest()
            return password_hash_check == stored_hash
        except ValueError:
            return False

    @staticmethod
    def get_user_by_id(db: Session, user_id: int):
        """根据用户ID获取用户信息"""
        query = text("SELECT * FROM us_users WHERE id = :user_id AND is_active = 1")
        result = db.execute(query, {"user_id": user_id})
        return result.fetchone()

    @staticmethod
    def update_user_password(db: Session, user_id: int, new_password_hash: str) -> bool:
        """更新用户密码"""
        try:
            query = text("""
                UPDATE us_users 
                SET password_hash = :password_hash, updated_at = :updated_at 
                WHERE id = :user_id
            """)
            result = db.execute(query, {
                "password_hash": new_password_hash,
                "updated_at": datetime.now(),
                "user_id": user_id
            })
            db.commit()
            return result.rowcount > 0
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def change_password(
        db: Session,
        user_id: int,
        current_password: str,
        new_password: str
    ) -> Tuple[bool, str]:
        """
        修改用户密码

        Args:
            db: 数据库会话
            user_id: 用户ID
            current_password: 当前密码
            new_password: 新密码

        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        # 1. 获取用户信息
        user = PasswordService.get_user_by_id(db, user_id)
        if not user:
            return False, "用户不存在或已被禁用"

        # 2. 验证当前密码
        if not PasswordService.verify_password(current_password, user.password_hash):
            return False, "当前密码错误"

        # 3. 检查新密码是否与当前密码相同
        if PasswordService.verify_password(new_password, user.password_hash):
            return False, "新密码不能与当前密码相同"

        # 4. 生成新密码哈希
        new_password_hash = PasswordService.hash_password(new_password)

        # 5. 更新密码
        try:
            success = PasswordService.update_user_password(db, user_id, new_password_hash)
            if success:
                return True, "密码修改成功"
            else:
                return False, "密码修改失败，请重试"
        except Exception as e:
            return False, f"密码修改失败：{str(e)}"

    @staticmethod
    def check_password_strength(password: str) -> Dict:
        """
        检查密码强度

        Returns:
            Dict: 包含强度信息的字典
        """
        requirements = {
            "min_length": len(password) >= 8,
            "has_letter": bool(re.search(r'[A-Za-z]', password)),
            "has_number": bool(re.search(r'\d', password)),
            "has_special": bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password)),
            "has_upper": bool(re.search(r'[A-Z]', password)),
            "has_lower": bool(re.search(r'[a-z]', password))
        }

        # 计算强度分数
        score = sum([
            requirements["min_length"],
            requirements["has_letter"],
            requirements["has_number"],
            requirements["has_special"],
            requirements["has_upper"],
            requirements["has_lower"]
        ])

        # 确定强度等级
        if score <= 2:
            strength_level = "弱"
        elif score <= 4:
            strength_level = "中"
        else:
            strength_level = "强"

        # 生成改进建议
        suggestions = []
        if not requirements["min_length"]:
            suggestions.append("密码长度至少8位")
        if not requirements["has_letter"]:
            suggestions.append("添加字母")
        if not requirements["has_number"]:
            suggestions.append("添加数字")
        if not requirements["has_special"]:
            suggestions.append("添加特殊字符（可选，但推荐）")
        if not requirements["has_upper"]:
            suggestions.append("添加大写字母（推荐）")
        if not requirements["has_lower"]:
            suggestions.append("添加小写字母（推荐）")

        # 基本要求：长度、字母、数字
        is_valid = (
            requirements["min_length"] and
            requirements["has_letter"] and
            requirements["has_number"]
        )

        return {
            "is_valid": is_valid,
            "strength_level": strength_level,
            "requirements": requirements,
            "suggestions": suggestions,
            "score": score
        }