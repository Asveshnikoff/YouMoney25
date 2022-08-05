import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')


# <class 'tuple'> <class 'list'> <class 'tuple'>
def circle_diag(userid: int, labels: tuple, sizes: list, explode: tuple, textdat: str):
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, explode=explode, shadow=False, startangle=90, counterclock=False, autopct='%.0f%%',
            wedgeprops=dict(width=0.3))
    # значения, подписи, отступы, тень, поворот, по часовой стрелке, проценты, дырка внутри
    ax1.axis('equal')
    ax1.text(0, -0.08, f'Всего:\n{sum(sizes)} руб.', horizontalalignment='center')
    ax1.text(1.75, -1.35, f'Создано @YouMoney25\nТвой персональный финансовый бот', fontsize=7, color='red', alpha=0.9,
             horizontalalignment='right')
    # текст, размер, цвет, прозрачность, выравнивание
    ax1.set_title(f'Расходы за {textdat}', fontweight='bold', pad=20)
    # ax1.legend(loc='upper right', bbox_to_anchor=(1, 1))
    # ax1.set_title('Всего:\n100 руб.', x=0.5, y=0.45)
    plt.savefig(f'{userid}_png')
    return
