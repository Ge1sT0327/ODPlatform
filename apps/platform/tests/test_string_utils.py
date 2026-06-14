from odp_platform.common.string_utils import display_width, format_table_row

def test_display_width_cjk():
    assert display_width("hello") == 5
    assert display_width("你好") == 4
    assert display_width("hello你好") == 9

def test_format_table_row():
    row = format_table_row(["ID", "名称", "值"], [4, 8, 6])
    assert "ID" in row
    assert "|" in row
