#!/bin/bash

# Имя файла для вывода
output_file="output.txt"

# Удаляем старый файл вывода, если он существует
rm -f "$output_file"

# Поиск файлов с расширением .html и вывод их содержимого с указанием пути к файлу
find . -type d -name ".git" -prune -o -type f -name "*.html" -print0 | xargs -0 -I {} sh -c 'echo -e "\n\nFile: {}\n" >> "$0"; cat "{}" >> "$0"' "$output_file"

echo "Содержимое всех файлов с расширением .html собрано в $output_file"