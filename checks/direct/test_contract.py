from conftest import CONTRACT
URLS=['https://regulator.example/recall/lot7','https://maker.example/notices/lot7']
def mocks(vm,answer='{"action":"RECALL","affected_lots":["LOT-7"],"conflict_source_indexes":[],"rationale":"Both records identify the lot.","confidence":94}'):
 vm.strict_mocks=True;vm.check_pickling=True
 vm.mock_web(r'regulator\.example',{'status':200,'body':'Official recall: product P, lot LOT-7, region North.'})
 vm.mock_web(r'maker\.example',{'status':200,'body':'Safety notice confirms LOT-7 must be recalled.'})
 vm.mock_llm(r'.*Recall safety adjudication.*',answer)
def test_full_lifecycle_preserves_sources(direct_vm,direct_deploy):
 c=direct_deploy(CONTRACT);mocks(direct_vm);c.open_case(' rc-7 ','Product P','LOT-7','North',URLS);c.adjudicate('RC-7')
 case=c.get_case(' rc-7 ');assert case['status']=='FINAL' and case['sources']==URLS and len(case['digests'])==2
 assert c.get_verdict('RC-7')['action']=='RECALL'
 with direct_vm.expect_revert('already adjudicated'):c.adjudicate('RC-7')
def test_duplicate_sources_ids_and_bad_hosts_rejected(direct_vm,direct_deploy):
 c=direct_deploy(CONTRACT);c.open_case('A','Product P','L1','North',URLS)
 with direct_vm.expect_revert('duplicate case id'):c.open_case(' a ','Product P','L1','North',URLS)
 with direct_vm.expect_revert('distinct HTTPS'):c.open_case('B','Product P','L1','North',[URLS[0],URLS[0]])
 with direct_vm.expect_revert('valid HTTPS'):c.open_case('C','Product P','L1','North',['https://good.example/a','https://good.example@evil.test/a'])
def test_forged_leader_attribution_fails(direct_vm,direct_deploy):
 c=direct_deploy(CONTRACT);mocks(direct_vm);c.open_case('X','Product P','LOT-7','North',URLS);result=c._investigate(c.cases['X']);direct_vm.mock_llm(r'.*Independently verify.*','{"valid":true}');assert direct_vm.run_validator(leader_result=result) is True;forged=dict(result);forged['digests']=list(reversed(result['digests']))
 assert direct_vm.run_validator(leader_result=forged) is False
