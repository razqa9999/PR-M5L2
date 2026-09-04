import sqlite3
import matplotlib

matplotlib.use('Agg')  # Menginstal backend Matplotlib untuk menyimpan file dalam memori tanpa menampilkan jendela
import matplotlib.pyplot as plt
import cartopy.crs as ccrs  # Mengimpor modul yang akan memungkinkan kita bekerja dengan proyeksi peta
import cartopy.feature as cfeature

class DB_Map():
    def __init__(self, database):
        self.database = database  # Menginisiasi jalur database

    def create_user_table(self):
        conn = sqlite3.connect(self.database)  # Menghubungkan ke database
        with conn:
            # Membuat tabel, jika tidak ada, untuk menyimpan kota pengguna
            conn.execute('''CREATE TABLE IF NOT EXISTS users_cities (
                                user_id INTEGER,
                                city_id TEXT,
                                FOREIGN KEY(city_id) REFERENCES cities(id)
                            )''')
            conn.commit()  # Menyimpan perubahan

    def add_city(self, user_id, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            # Mencari kota dalam database berdasarkan nama
            cursor.execute("SELECT id FROM cities WHERE city=?", (city_name,))
            city_data = cursor.fetchone()
            if city_data:
                city_id = city_data[0]
                # Menambahkan kota ke daftar kota pengguna
                conn.execute('INSERT INTO users_cities VALUES (?, ?)', (user_id, city_id))
                conn.commit()
                return 1  # Menunjukkan bahwa operasi berhasil
            else:
                return 0  # Menunjukkan bahwa kota tidak ditemukan

    def select_cities(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            # Memilih semua kota pengguna
            cursor.execute('''SELECT cities.city 
                            FROM users_cities  
                            JOIN cities ON users_cities.city_id = cities.id
                            WHERE users_cities.user_id = ?''', (user_id,))
            cities = [row[0] for row in cursor.fetchall()]
            return cities  # Mengembalikan daftar kota pengguna

    def get_coordinates(self, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            # Mendapatkan koordinat kota berdasarkan nama
            cursor.execute('''SELECT lat, lng
                            FROM cities  
                            WHERE city = ?''', (city_name,))
            coordinates = cursor.fetchone()
            return coordinates  # Mengembalikan koordinat kota

    def create_graph(self, path, cities, marker_color="red"):
        figure, ax = plt.subplots(subplot_kw={"projection": ccrs.PlateCarree()})
        ax.set_global()
        ax.add_feature(cfeature.OCEAN, facecolor="#b9dff2")
        ax.add_feature(cfeature.LAND, facecolor="#d9c7a5")
        ax.add_feature(cfeature.LAKES, facecolor="#b9dff2", edgecolor="#6b9db5")
        ax.add_feature(cfeature.RIVERS, edgecolor="#6b9db5")
        ax.add_feature(cfeature.BORDERS, linestyle=":", edgecolor="#555555")
        ax.coastlines(color="#444444")

        for city in cities:
            coord = self.get_coordinates(city)
            if coord is None:
                continue

            ax.plot(coord[1], coord[0], marker='o', color=marker_color, markersize=6, transform=ccrs.Geodetic())

            # plt.plot([ny_lon], [ny_lat],
            #                 color='blue', linewidth=2, marker='o',
            #                 transform=ccrs.Geodetic(),
            #                 )

            # plt.text(ny_lon - 3, ny_lat - 12, city,
            #                 horizontalalignment='right',
            #                 transform=ccrs.Geodetic())

        figure.tight_layout()
        figure.savefig(path, format="png")
        plt.close(figure)

    def draw_distance(self, city1, city2):
        figure, ax = plt.subplots(subplot_kw={"projection": ccrs.PlateCarree()})
        ax.stock_img()

        city1_coordinates = self.get_coordinates(city1)
        city2_coordinates = self.get_coordinates(city2)
        if city1_coordinates is None or city2_coordinates is None:
            plt.close(figure)
            raise ValueError("Kota tidak ditemukan dalam database")

        city1_lat, city1_lon = city1_coordinates
        city2_lat, city2_lon = city2_coordinates

        ax.plot([city1_lon, city2_lon], [city1_lat, city2_lat],
                color='blue', linewidth=2, marker='o',
                transform=ccrs.Geodetic(),
                )

        ax.plot([city1_lon, city2_lon], [city1_lat, city2_lat],
                color='gray', linestyle='--',
                transform=ccrs.PlateCarree(),
                )

        ax.text(city1_lon - 3, city1_lat - 12, city1,
                horizontalalignment='right',
                transform=ccrs.Geodetic())

        ax.text(city2_lon + 3, city2_lat - 12, city2,
                horizontalalignment='left',
                transform=ccrs.Geodetic())

        try:
            figure.savefig("distance.png")
        finally:
            plt.close(figure)


if __name__ == "__main__":
    m = DB_Map("database.db")  # Membuat objek yang akan berinteraksi dengan database
    m.create_user_table()   # Membuat tabel dengan kota pengguna, jika tidak sudah ada
