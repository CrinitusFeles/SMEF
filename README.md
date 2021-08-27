# Система мониторинга электрического поля

Графический интерфейс для монитора электрической компоненты поля - _FI7000_

![picture 21](images/sensor%20.png)  

## Установка

```sh 
python3 -m pip install https://api.github.com/repos/CrinitusFeles/SMEF/tarball/main 
```
or run install_packet.bat (for Windows)


## Использование

При наличии оборудования запустить в терминале

```sh 
python3 smef
```

При отсутствии оборудования запустить в терминале 

```sh 
python3 smef --demo
```

или 

```sh 
python3 smef -d
```

Запущенный процесс будет эмулировать работу оборудования и генерировать случайные данные для поля.


При успешном запуске появится главное окно программы

<!-- ![picture 12](images/main_window0%20.png)   -->
![picture 1](images/main_window_dark%20.png)  


### Первый запуск

Если программа запускается впервые, то в текущей директории будет создан конфигурационный файл с настройками, который будет хранить в себе редко изменяемые пользователем параметры. 

При первом запуске программы необходимо открыть окно с настройками подключения соответствующей кнопкой в верхней части главного окна.


<!-- ![picture 13](images/connection_settings_window%20.png) -->
![picture 2](images/connections_dark%20.png)  


По умолчанию программа ожидает работы с эмулятором. При наличии подключения оборудования необходимо прописать ip адрес терминального сервера. При изменении настроек портов терминального сервера, в программе также нужно указать номера новых портов. Изменить номера портов терминального сервера можно на его веб-странице. Для этого нужно прописать в адресную строку браузера адрес терминального сервера.

_Раздел с настройками генератора - заглушка для возможного будущего функционала._

После внесения изменений нажимаем кнопку "_Приниять_". Новые настройки сохранятся в конфигурационный файл и окно с настройками подключения закроется.

### Новый сеанс

Теперь можно начинать новый сеанс. Для этого необходимо нажать соответствующую кнопку в верхней части главного окна.


В появившемся окне прежде всего необходимо обратить внимание на раздел "Подключенные датчики". Если checkbox датчика неактивен, то это говорит о невозможности установить с ним соединение. Проверьте физическое подключение данного датчика и нажмите кнопку "Обновить" для перепроверки наличия подключенных датчиков.

Если все checkbox'ы датчиков неактивны как на картинке ниже, то это значит, что был указан неверный адрес терминального сервера (или программа была запущена не в демонстрационном режиме). 


![picture 4](images/new_session_dark%20.png)  


При корректно указанных данных терминального сервера вы увидите следующее окно:

<!-- ![picture 14](images/new_session_window%20.png)   -->
![picture 5](images/new_session_dark2%20.png)  


При первом запуске программы в текущей директории будет создана папка _output_, куда будут сохраняться данные сеансов, а также папка _event_logs_, куда будут писаться логи.

По необходимости можно изменить папку сохранения данных сеанса, прописав путь вручную, или, нажав кнопку "..." рядом с полем ввода и выбрав папку в появившемся меню. Если указать относительный путь, то папка будет создана в текущей директории. При указании ранее несуществующего пути, он будет создан со всеми подкаталогами.

Также необходимо обязательно указать имя файла. Это можно сделать вручную или сгенерировать кнопкой рядом с полем ввода.

Описание сессии не является обязательным параметром, но может быть полезным при последующем просмотре этого сеанса.

В разделе "Подключенные датчики" можно отметить только те, что необходимы для данного сеанса.

После указания всех необходимых данных нажмите кнопку "_Принять_". Новые настройки сохранятся в конфигурационный файл и окно с настройками нового сеанса закроется.

## Запуск измерений

После создания нового сеанса в главном окне разблокируются кнопки "_Старт_" и "_Стоп_" в разделе "_Управление сеансом_".

При нажатии на кнопку "_Старт_" начнется опрос ранее указанных датчиков. По данным датчиков будут строиться графики в реальном времени. Текст кнопки "_Старт_" изменится на "_Пауза_". При повторном нажатии можно временно остановить опрос датчиков, а текст кнопки изменится на "_Старт_".

Период измерений задается полем ввода в разделе "Период опроса датчиков".

При нажатии на кнопку "_Стоп_" сеанс будет завершен и полностью остановлен, а кнопки "_Старт_" и "_Стоп_" заблокируются. Для начала нового сеанса см. предыдущий пункт.

<!-- ![picture 11](images/main_window%20.png)   -->
<!-- ![picture 6](images/main_window_measure_dark%20.png)   -->
![picture 8](images/main_window_measure_dark2%20.png)  


### Элементы управления графиком

По умолчанию под курсом мыши отображается зеленое перекрестие с подписью данных датчиков, лежащих под вертикальной линией перекрестия. При двойном нажатии на левую кнопку мыши перекрестие зафиксирует свое положение и не будет следовать за курсором (функционал для скриншотов). При необходимости перекрестие можно отключить checkbox'ом "_Маркеры данных_" в разделе "_Параметры нормы и маркеров_".

При движении мыши с зажатой левой кнопкой (или зажатым колесом) происходит перетаскивание графика.

Окно легенд можно перемещать с зажатой левой кнопкой мыши.

При движении мыши с зажатой правой кнопкой и происходит масштабирование графика. Также масштибирование осуществляется колесиком мыши. При этом сбивается автоматическое масштабирование. Для включения автоматического масштабирования наведите курсор на окно с графиками. В нижнем левом углу появляется кнопка сброса масштабирования при нажатии на которую графики растянутся по размеру окна. 

![picture 9](images/scale_button%20.png)  


Того же самого можно добиться, вызвав контекстное меню одиночным нажатием правой кнопкой мыши и, выбрав пункт "_View all_".

![picture 10](images/context_menu%20.png)  


При использовании версии библиотеки pyqtgraph новее 0.11 доступен функционал скрытия графиков нажатием на цветную полоску в окне легенд напротив нужного графика. Для AstraLinux этот функционал был продублирован в виде checkbox'ов в разделе "_Отображение графиков_". 

Поле ввода в разделе "_Заголовок графика_" позволяет задать графику заголовок, который также будет отображаться на скриншотах.

Для добавления визуальной границы нормы данных можно включить отображение бесконечной горизонтальной линии в разделе "_Параметры нормы и маркеров_" с помощью checkbox'а "_Норма_". Соседнее поле ввода задает величину нормы. Данная линия служит только для визуального представления и при выходе данных за норму ничего не произойдет.

По мере опроса датчиков данные будут добавляться на график в течение времени указанного в разделе "_Размер скользящего окна_". При превышении лимита будут поочередно удаляться самые старые данные для освобождения места новым. Размер скользящего окна может быть больше года, но нет гарантии стабильной работы операционной системы на таких продолжительных промежутках непрерывной работы.

Справа от окна с графиками расположена таблица, где указаны минимальное, максимальное и среднее значение каждого датчика для текущей сессии.

### Единицы измерения

В разделе "_Единицы измерения_" можно выбрать в каких единицах отображать данные датчиков. По умолчанию с датчиков приходят данные размерностью $В/м$. Для перевода их в другие единицы использовались следующие соотношения:

$$В/м \rightarrow дБмкВ/м:      E_{дБмкВ/м} = 20 * \lg(E_{В/м} * 10^6),     if   E_{В/м} == 0\rightarrow E_{В/м} = 0.001$$

$$В/м \rightarrow  Вт/м^2:      E_{Вт/м^2} = E_{В/м} / 377.$$
### Копирование данных

В разделе "_Копирование данных_" находятся две кнопки для сохранения изображения графика или текстовых данных в буфер обмена. Используется следующим образом: 
1) отмасштибировать интересуемый участок
2) нажимаеть кнопку кнопку "_Копировать график_" или "_Копировтаь данные_"
3) комбинацией клавиш _CTRL-V_ вставить данные/изображение.

## Просмотр сохраненного сеанса

В любой момент можно открыть в окне просмотра текущий сеанс или ранее сохраненный. Для этого нажмите на кнопку "_Открыть сохраненный сеанс_" в верхней части главного окна.

В новом окне вы увидите файловую систему директории программы. Далее нужно выбрать _.csv_ файл интересуемой сессии в папке _output/_ или в той, которую вы прописывали как путь сохранения сессии в окне создания нового сеанса.

После выбора файла сессии откроется окно просмотра сессии:

<!-- ![picture 2](images/session_viewer%20.png)   -->
![picture 7](images/session_viewer_dark%20.png)  


Данное окно почти не отличается от главного за исключением отсутствия ненужных элементов управления и наличием двухдиапазонного ползунка под графиков с помощью которого можно делать срез данных. По умолчанию в нем установлен полный диапазон. Для уменьшения диапазона потяните левый или правый ползунок. При двойном нажатии на элемент будет восстановлен полный диапазон. При открытии файла с очень большим числом данных для улучшения отзывчивости итнтерфейса можно также использовать срез данных.

Также в данном окне находится поле с описанием сессии. Здесь отображается текст, который был введен в поле "Описание сессии" на этапе создания новой сессии.

<style>  
img {
  display:block;
  margin: 0 auto;
}
</style>
