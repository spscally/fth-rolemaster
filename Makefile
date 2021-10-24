venv: requirements.txt
	python -m venv venv
	powershell -noexit -executionpolicy bypass venv/Scripts/Activate.ps1; pip install -r requirements.txt

reports:
	mkdir reports/

tt:
	mkdir tt/

clean:
	powershell Remove-Item -Recurse -Force venv