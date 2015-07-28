{
    'name': 'Vịt con Sale & Purchase',
    'category': 'sale_purchase',
    'summary': 'Quản lý Kinh Doanh',
    'version': '1.0',
    'description': """
        Module Quản lý bán hàng, đặt hàng.\n
        --\n
        Author: Trần Anh Dũng (Mr)\n
        Hanoi University of Science and Technology\n
        Phone: 0989 345 654\n
        Email: trananhdung17@gmail.com

    """,
    'author': 'trananhdung17',
    'depends': ['base', 'product_pricelist'],
    'installable': True,
    'data': [
        'datas/views.xml',
        'datas/datas.xml',
        'datas/security.xml',
        'datas/reports.xml',
        'datas/ir.model.access.csv'
    ],
    'demo': [],
    'qweb': [],
    'application': True,
}