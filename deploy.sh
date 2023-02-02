. venv/bin/activate

git checkout dev

pip freeze > requirements.txt

git commit -m 'deployment dependencies'

git push

git checkout main

git merge dev

git push

