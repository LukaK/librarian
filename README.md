<h1 align="center"> Hmmmm </h1>

### Introduction

### Instalation
```
# create stack
sam deploy --gudied --template-file sam/service.sam.yaml

# delete stack
sam delete --stack-name <stack name>
```

### Development
```
gem install cfn-nag
pre-commit install --hook-type pre-commit pre-push
```
