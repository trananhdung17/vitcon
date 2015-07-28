{
    'name': 'Vịt con Product',
    'category': 'product',
    'summary': 'Thiết lập sản phẩm bán hàng',
    'version': '1.0',
    'description': """
        Module cấu hình các mẫu sản phẩm và quản lý sản phẩm bán hàng.\n
        --\n
        Author: Trần Anh Dũng (Mr)\n
        Hanoi University of Science and Technology\n
        Phone: 0989 345 654\n
        Email: trananhdung17@gmail.com\n

    """,
    'author': 'trananhdung17',
    'depends': ['base', 'mail'],
    'installable': True,
    'data': [
        'datas/views.xml',
        'datas/datas.xml',
        'datas/security.xml',
        'datas/ir.model.access.csv'
    ],
    'demo': [],
    'qweb': [],
    'application': True,
}