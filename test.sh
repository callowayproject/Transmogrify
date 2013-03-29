cd `dirname $0`
pip install mock webob
cd example
python ./manage.py test transmogrify
