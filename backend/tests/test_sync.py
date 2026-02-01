"""
EDINETデータ同期機能のテスト
"""

import io
import zipfile

from backend.sync_edinet import extract_holding_data_from_csv


def create_test_zip(csv_content: str, filename: str = "test.csv") -> bytes:
    """テスト用ZIPファイルを作成"""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(filename, csv_content.encode("utf-16"))
    return zip_buffer.getvalue()


class TestExtractHoldingDataFromCsv:
    """extract_holding_data_from_csv関数のテスト"""

    def test_extract_holding_data_success(self):
        """正常系: 保有データが正しく抽出される"""
        # EDINET形式のCSV内容（保有目的は「保有の目的」で検索）
        csv_content = "項目名\t値\n株券等保有割合（％）\t71.4\n保有株券等の数（総数）\t21,398,920\n保有の目的\t政策投資のため\n"
        zip_content = create_test_zip(csv_content)

        result = extract_holding_data_from_csv(zip_content)

        assert result["holding_ratio"] == 71.4
        assert result["shares_held"] == 21398920
        assert result["purpose"] == "政策投資のため"

    def test_extract_holding_data_with_percentage_symbol(self):
        """保有割合に%記号が含まれる場合"""
        csv_content = "項目名\t値\n株券等保有割合（％）\t5.5%\n保有株券等の数（総数）\t1,000,000\n保有目的\t純粋投資のため\n"
        zip_content = create_test_zip(csv_content)

        result = extract_holding_data_from_csv(zip_content)

        assert result["holding_ratio"] == 5.5
        assert result["shares_held"] == 1000000

    def test_extract_holding_data_ratio_as_decimal(self):
        """保有割合が0-1の小数で格納されている場合"""
        csv_content = "項目名\t値\n株券等保有割合（％）\t0.055\n保有株券等の数（総数）\t100000\n"
        zip_content = create_test_zip(csv_content)

        result = extract_holding_data_from_csv(zip_content)

        # 0.055 → 5.5%に変換される
        assert result["holding_ratio"] == 5.5

    def test_extract_holding_data_empty_zip(self):
        """空のZIPファイルの場合"""
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED):
            pass  # 空のZIP
        empty_zip = zip_buffer.getvalue()

        result = extract_holding_data_from_csv(empty_zip)

        assert result["holding_ratio"] is None
        assert result["shares_held"] is None
        assert result["purpose"] is None

    def test_extract_holding_data_no_csv_in_zip(self):
        """ZIP内にCSVファイルがない場合"""
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("test.txt", "not a csv")
        zip_content = zip_buffer.getvalue()

        result = extract_holding_data_from_csv(zip_content)

        assert result["holding_ratio"] is None
        assert result["shares_held"] is None
        assert result["purpose"] is None

    def test_extract_holding_data_invalid_csv_format(self):
        """CSVの形式が不正な場合"""
        # "項目名"と"値"の列がない
        csv_content = "列1\t列2\t列3\n値1\t値2\t値3\n"
        zip_content = create_test_zip(csv_content)

        result = extract_holding_data_from_csv(zip_content)

        assert result["holding_ratio"] is None
        assert result["shares_held"] is None
        assert result["purpose"] is None

    def test_extract_holding_data_partial_data(self):
        """一部のデータのみ存在する場合"""
        csv_content = "項目名\t値\n株券等保有割合（％）\t10.5\n"  # sharesとpurposeなし
        zip_content = create_test_zip(csv_content)

        result = extract_holding_data_from_csv(zip_content)

        assert result["holding_ratio"] == 10.5
        assert result["shares_held"] is None
        assert result["purpose"] is None
