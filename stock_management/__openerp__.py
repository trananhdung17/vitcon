# __author__ = trananhdung17
{
    'name': 'Vịt con Stock',
    'category': 'stock',
    'summary': 'Quản lý kho hàng',
    'version': '1.0',
    'description': """
        Module quản lý kho hàng.\n
        --\n
        Author: Trần Anh Dũng (Mr)\n
        Hanoi University of Science and Technology\n
        Phone: 0989 345 654\n
        Email: trananhdung17@gmail.com
    """,
    'author': 'trananhdung17',
    'depends': ['product_pricelist', 'sale_and_purchase'],
    'installable': True,
    'data': [
        'datas/views.xml'
        'datas/security.xml',
        'datas/ir.model.access.csv'
    ],
    'demo': [],
    'qweb': [],
    'application': True,
}