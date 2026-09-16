# Supermercado Caixa — Django Backend

Backend profissional para um sistema de caixa de supermercado, desenvolvido com Django 5.2 LTS, Django REST Framework, Simple JWT, SQLite e ReportLab.

## Requisitos

- Python 3.12+
- Django 5.2 LTS
- SQLite
- pip

## Instalação

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
python manage.py makemigrations core products sales
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

## Acessos de demonstração

- admin: `admin@caixa.local` / `Admin@12345`
- gerente: `gerente@caixa.local` / `Gerente@12345`
- caixa: `caixa@caixa.local` / `Caixa@12345`

Altere essas credenciais antes de qualquer uso real.

## Principais endpoints

- `POST /api/auth/token/`
- `POST /api/auth/token/refresh/`
- `GET|POST /api/usuarios/`
- `GET|POST /api/produtos/`
- `GET|POST /api/vendas/`
- `GET|POST /api/itens-venda/`
- `GET /api/relatorios/vendas/`
- `GET /api/relatorios/produtos/`
- `GET /api/vendas/<id>/cupom/`

Também existe `/admin/` para administração do sistema.

## Arquitetura

- `core`: configurações, autenticação e infraestrutura compartilhada.
- `products`: catálogo e estoque.
- `sales`: vendas e itens de venda.
- `reports`: consultas e análises.
- `receipts`: geração do cupom fiscal simplificado em PDF.

As regras de negócio de venda ficam em `sales/services.py`, evitando colocar lógica transacional complexa diretamente nas views.

## Regras importantes

1. Senhas nunca são armazenadas em texto puro; o User do Django utiliza os hashers nativos.
2. Finalização de venda ocorre dentro de `transaction.atomic()`.
3. Estoque é bloqueado com `select_for_update()` durante a finalização.
4. Venda finalizada não pode ser alterada diretamente.
5. O total da venda é calculado no servidor.
6. Valores monetários usam `Decimal`, nunca `float`.
7. Endpoints exigem autenticação e permissões.
8. CSRF, XSS, SQL injection e proteção de sessão seguem os mecanismos nativos do Django/DRF.
9. Segredos ficam em variáveis de ambiente no arquivo `.env` (não versionar `.env`).
10. O SQLite atende o desenvolvimento inicial; para produção recomenda-se PostgreSQL.

## Testes

```bash
python manage.py test
```

## Qualidade

O projeto segue PEP 8, nomes explícitos, funções pequenas, separação de responsabilidades, serviços para regras de domínio, serializers para validação de entrada/saída e testes automatizados para os casos críticos.
