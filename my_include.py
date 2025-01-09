import pandas as pd
import streamlit as st
from charset_normalizer import from_bytes
from io import StringIO

def detect_encoding(file):
    """charset-normalizerを使用してエンコーディングを検出"""
    raw_data = file.read()
    file.seek(0)
    result = from_bytes(raw_data).best()
    return result.encoding if result else None

def main():
    st.title("CSVファイル集計アプリ")
    st.write("アップロードされたCSVファイルから商品と同梱物の合計点数および追加数量を計算します。")

    # ファイルアップローダー
    uploaded_file = st.file_uploader("CSVファイルをアップロードしてください", type=["csv"])

    if uploaded_file:
        # エンコーディングを検出
        encoding = detect_encoding(uploaded_file)
        st.write(f"検出されたエンコーディング: {encoding}")

        try:
            # ファイルをデコードしてデータフレームに読み込む
            raw_data = uploaded_file.read()
            decoded_data = raw_data.decode(encoding, errors="replace")
            df = pd.read_csv(StringIO(decoded_data))

            # CSVファイルの列名を表示
            st.write("CSVファイルの列名:", df.columns.tolist())

            # 列名のマッピングを定義
            column_mapping = {
                "受注番号": "B",
                "同梱物": "DY",
                "購入商品（個数）": "K"
            }

            # 列名をマッピング
            df.rename(columns=column_mapping, inplace=True)

            # 必要な列名
            required_columns = ["B", "DY", "K"]

            # 必要な列が存在するか確認
            if all(col in df.columns for col in required_columns):
                # 必要なデータを抽出
                extracted_df = df[required_columns].copy()
                extracted_df.rename(columns={"B": "受注番号", "DY": "同梱物フラグ", "K": "数量"}, inplace=True)

                # 商品と同梱物をグループ化して合計数量を計算
                summary = (
                    extracted_df.groupby("受注番号")
                    .apply(lambda x: pd.Series({
                        "商品総数": x.loc[x["同梱物フラグ"] == 0, "数量"].sum(),
                        "同梱物総数": x.loc[x["同梱物フラグ"] == 1, "数量"].sum()
                    }))
                    .reset_index()
                )

                # 追加数量を計算
                summary["商品追加数量"] = summary["商品総数"].apply(lambda x: max(0, x - 4))
                summary["同梱物追加数量"] = summary["同梱物総数"].apply(lambda x: max(0, x - 5))

                # 結果を表示
                st.write("計算結果:")
                st.dataframe(summary)

                # CSVファイルをダウンロード可能にする
                csv_data = summary.to_csv(index=False, encoding="utf-8-sig")
                st.download_button(
                    label="結果をCSVでダウンロード",
                    data=csv_data,
                    file_name="result.csv",
                    mime="text/csv"
                )
            else:
                missing_columns = [col for col in required_columns if col not in df.columns]
                st.error(f"以下の必要な列が見つかりませんでした: {', '.join(missing_columns)}")

        except UnicodeDecodeError as e:
            st.error(f"エンコーディングのデコード中にエラーが発生しました: {e}")
        except pd.errors.ParserError as e:
            st.error(f"CSVの解析中にエラーが発生しました: {e}")
        except Exception as e:
            st.error(f"予期しないエラーが発生しました: {e}")

if __name__ == "__main__":
    main()
