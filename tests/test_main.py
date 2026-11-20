from invoiceflow.main import main


def test_main(capsys):
    main()

    captured = capsys.readouterr()

    assert "InvoiceFlow" in captured.out
    assert "initialized successfully" in captured.out