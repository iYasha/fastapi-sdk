version:
	@poetry version $(v)
	@git add *
	@git commit -m "v$$(poetry version -s)"
	@git tag v$$(poetry version -s)
	@git push --set-upstream origin main
	@git push --tags origin main