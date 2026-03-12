<!-- docs\PROJECT_MAP.md -->

# Kakeibo Analytics App - Project Map

## プロジェクト概要

目的：
- クレカCSVを取り込み
- 明細を分類（な / ゆ / 共有）
- 月次集計
- 将来予測
- 可視化

使用技術：
- Django
- PostgreSQL（根拠：.env の DATABASE_URL が `postgresql://...`。  
  settings.py で DATABASE_URL を dj_database_url.parse() して DB 接続している）
- CSS
- 線形回帰（予測）

---

## アプリ構成
※「アプリ構成」は “画面の一覧” ではなく「そのURL/処理を担当する Djangoアプリ（views / models）」の責務を書く。

---
### account
役割：  
アプリのメインUIを担当するアプリ。  

Home / CSV Import / EDA / Zones / Prediction など  
主要画面の表示を行う。

主な処理：
- Home画面表示
- CSV Import画面
- EDA画面
- Zones画面
- Prediction画面
- ログイン処理

関連ファイル：
- views.py
- templates/account/*
- services/*

---
### services（account/services）

役割：  
Viewから分析ロジックを分離するサービス層。

データ集計・統計処理・予測処理など  
ビジネスロジックを担当する。

主なサービス：

- home_service.py  
  Home画面用データ集計

- eda_service.py  
  支出統計の計算

- zones_service.py  
  支出ゾーン判定

- prediction_service.py  
  月次支出の線形回帰予測

- prediction_breakdown_service.py  
  予測の内訳計算

- event_detection_service.py  
  特殊支出イベント検出

---
### utils

役割：  
アプリ全体で利用する共通ユーティリティ。

主な処理：

- date_utils.py
  日付処理

- guest_utils.py
  Guestユーザー用マスキング

- stats_utils.py
  簡易統計処理

---
## transactions

役割：  
支出データ管理アプリ。

クレジットカード明細の保存・編集・分類を担当する。

主な処理：

- Transactionモデル管理
- 支出一覧表示
- カテゴリ分類
- メンバー割当
- CSVデータ登録

関連ファイル：

- models.py
- views.py
- forms.py
- rules.py
- templates/transactions/*

---
### CSV Import

役割：  
クレジットカード明細CSVを取り込み、  
TransactionデータとしてDBへ登録する。

処理フロー：

CSVアップロード  
↓  
account.views.csv_import  
↓  
Transaction作成  
↓  
DB保存

---
### Batch Import

役割：  
過去CSVの一括インポート用スクリプト。

関連ファイル：

transactions/management/commands/import_past_csv.py

---
### templatetags

役割：  
テンプレート用カスタムフィルター。

guest_filters.py  
Guestユーザー用データマスキング。

---
## members

役割：  
支出のメンバー管理。

支出データの「誰の支出か」を管理する。

---

## 主要モデル

### Transaction

| フィールド | 型 | 用途 |
|------------|----|------|
| id | AutoField | 明細の一意識別子（更新・行特定に使用） |
| date | DateField | 取引日 |
| shop | CharField | 店名 |
| amount | IntegerField | 金額 |
| member | FK(Member) | 支払者 |
| category | FK(Category) | 分類 |
| memo | TextField | 補足 |
| source_file | CharField | 取込元CSV |
| is_closed | Boolean | 確定フラグ |


---

## URL → View → Template 対応表

| URL                               | View                                  | Template                                      |
| --------------------------------- | ------------------------------------- | --------------------------------------------- |
| `/`                               | `account.views.home`                  | `account/home.html`                           |
| `/import/`                        | `account.views.csv_import`            | `account/csv_import.html`                     |
| `/eda/`                           | `account.views.eda`                   | `account/eda.html`                            |
| `/zones/`                         | `account.views.zones`                 | `account/zones.html`                          |
| `/prediction/`                    | `account.views.prediction`            | `account/prediction.html`                     |
| `/prediction/breakdown/<yyyymm>/` | `account.views.prediction_breakdown`  | `account/_prediction_breakdown.html`（HTML断片）  |
| `/transactions/`                  | `transactions.views.transaction_list` | `transactions/transaction_list.html`          |
| `/transactions/rows/`             | `transactions.views.transaction_rows` | `transactions/_transaction_rows.html`（HTML断片） |
| `/login/`                         | `LoginView`                           | `account/login.html`（urls.py側指定）              |
| `/logout/`                        | `LogoutView`                          | （テンプレなし：通常リダイレクト）                             |
| `/admin/`                         | admin                                 | （Django管理画面）                                  |

CSV取込の実処理は transactions.views.transaction_list(POST) 側で行う  
(accountの /import/ は画面のみ)

## 予測ロジック

入口：
- account/views.py → prediction()
- account/views.py → prediction_breakdown()

処理内容：
- Transactionから月次集計を生成
- 線形回帰で翌月予測
- walk-forwardで精度検証

## 分類ルール

入口：
- transactions/rules.py（shop/memo等から category/member を推定）
- 適用タイミング：transaction_list(POST) / または手動編集

## 一覧の部分更新
- /transactions/rows/ が HTML断片（_transaction_rows.html）を返す

---

## データの流れ

CSV取込  
↓  
UI Import（account.views）  
↓  
Transactionテーブル保存  
↓  
rules.py で自動分類  
↓  
transaction_list画面で手動修正  
↓  
prediction()で月次集計  
↓  
prediction.html表示  


---

## 今後の整理方針

- ロジックはservices.pyへ分離予定
- viewsは薄く保つ
- docsに設計を集約
