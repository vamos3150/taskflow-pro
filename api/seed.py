from __future__ import annotations
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from api import models


def seed(db: Session) -> None:
    if db.query(models.Project).count() > 0:
        return

    now = datetime.utcnow()
    projects = [
        models.Project(name="Webサイトリニューアル", color="#6366f1"),
        models.Project(name="モバイルアプリ開発",    color="#0ea5e9"),
        models.Project(name="マーケティング施策",    color="#f59e0b"),
        models.Project(name="社内業務改善",          color="#10b981"),
    ]
    db.add_all(projects)
    db.flush()

    p1 = projects[0]
    tasks_data = [
        # 未着手
        dict(project_id=p1.id, title="要件定義書の作成",      status="未着手", priority="高", assignee="山田 太郎",  due_date=now + timedelta(days=40), labels="ドキュメント"),
        dict(project_id=p1.id, title="競合サイトの調査",      status="未着手", priority="中", assignee="佐藤 花子",  due_date=now + timedelta(days=42)),
        dict(project_id=p1.id, title="ワイヤーフレームの作成", status="未着手", priority="中", assignee="鈴木 一郎",  due_date=now + timedelta(days=45)),
        dict(project_id=p1.id, title="コンテンツ構成案の作成", status="未着手", priority="低", assignee="田中 美咲",  due_date=now + timedelta(days=47)),
        dict(project_id=p1.id, title="デザインコンセプトの策定", status="未着手", priority="中", assignee="山田 太郎", due_date=now + timedelta(days=50)),
        # 進行中
        dict(project_id=p1.id, title="トップページのデザイン作成", status="進行中", priority="高", assignee="鈴木 一郎", due_date=now + timedelta(days=35), labels="デザイン,トップページ", description="トップページのデザインカンプを作成してください。PC版とスマートフォン版の両方をお願いします。"),
        dict(project_id=p1.id, title="下層ページのデザイン作成",  status="進行中", priority="中", assignee="田中 美咲",  due_date=now + timedelta(days=38), labels="デザイン"),
        dict(project_id=p1.id, title="コーディング（トップページ）", status="進行中", priority="高", assignee="伊藤 健太", due_date=now + timedelta(days=39), labels="コーディング"),
        dict(project_id=p1.id, title="お問い合わせフォームの実装", status="進行中", priority="中", assignee="伊藤 健太", due_date=now + timedelta(days=41)),
        # レビュー中
        dict(project_id=p1.id, title="スマートフォン表示の確認", status="レビュー中", priority="高", assignee="佐藤 花子", due_date=now + timedelta(days=3),  labels="テスト"),
        dict(project_id=p1.id, title="SEO対策の確認",           status="レビュー中", priority="中", assignee="山田 太郎", due_date=now + timedelta(days=4),  labels="SEO"),
        # 完了
        dict(project_id=p1.id, title="プロジェクトキックオフ",  status="完了", priority="高", assignee="山田 太郎", due_date=now - timedelta(days=30)),
        dict(project_id=p1.id, title="サイトマップの作成",      status="完了", priority="中", assignee="鈴木 一郎", due_date=now - timedelta(days=20)),
        dict(project_id=p1.id, title="ロゴ・画像素材の準備",   status="完了", priority="中", assignee="田中 美咲", due_date=now - timedelta(days=10)),
    ]

    task_objs = []
    for td in tasks_data:
        t = models.Task(**td)
        db.add(t)
        task_objs.append(t)
    db.flush()

    # サブタスクとコメント（トップページデザインタスク）
    top_task = task_objs[5]
    subtasks = [
        models.Subtask(task_id=top_task.id, title="デザインコンセプトの確認", done=True),
        models.Subtask(task_id=top_task.id, title="PC版デザインの作成",       done=True),
        models.Subtask(task_id=top_task.id, title="スマートフォン版デザインの作成", done=False),
        models.Subtask(task_id=top_task.id, title="デザインレビュー・修正",   done=False),
    ]
    db.add_all(subtasks)

    comment = models.Comment(
        task_id=top_task.id,
        author="山田 太郎",
        content="デザインコンセプトを共有します。ご確認をお願いします。",
        created_at=datetime.utcnow() - timedelta(hours=2),
    )
    db.add(comment)

    # モバイルアプリのタスクも少し追加
    p2 = projects[1]
    mobile_tasks = [
        dict(project_id=p2.id, title="ログイン画面実装",   status="進行中", priority="高", assignee="佐藤 花子", due_date=now + timedelta(days=10)),
        dict(project_id=p2.id, title="プッシュ通知対応",   status="未着手", priority="中", assignee="鈴木 一郎", due_date=now + timedelta(days=20)),
        dict(project_id=p2.id, title="API連携テスト",      status="レビュー中", priority="高", assignee="伊藤 健太", due_date=now + timedelta(days=5)),
        dict(project_id=p2.id, title="ストア申請",          status="未着手", priority="中", assignee="山田 太郎", due_date=now + timedelta(days=30)),
    ]
    for td in mobile_tasks:
        db.add(models.Task(**td))

    db.commit()
