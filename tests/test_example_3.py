import helperFuncs as hp

def test_example_3(tmpdir):
    testName="example_3"
    threshMLBL = 0.1
    threshLG =  1.0
    threshOG = 2.0
    [passNumAtoms,passMLBL,passLG,passOG,pass_report] = hp.runtest(tmpdir,testName,threshMLBL,threshLG,threshOG)
    assert passNumAtoms
    assert passMLBL
    assert passLG
    assert passOG
    assert pass_report

def test_example_3_No_FF(tmpdir):
    testName="example_3"
    threshMLBL = 0.1
    threshLG =  1.0
    threshOG = 2.0
    [passNumAtoms,passMLBL,passLG,passOG,pass_report] = hp.runtestNoFF(tmpdir,testName,threshMLBL,threshLG,threshOG)
    assert passMLBL
    assert passLG
    assert passOG
    assert pass_report
