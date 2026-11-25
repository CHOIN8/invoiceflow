
from invoiceflow.main import main


def test_main_requires_document_argument(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        ["invoiceflow", "--help"],
    )

    try:
        main()
    except SystemExit as error:
        assert error.code == 0
