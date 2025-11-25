#!/bin/bash

echo "Создаем 100 обращений..."
for i in $(seq 1 100); do
    phone="+79999$(printf '%06d' $i)"
    curl -s -X POST http://localhost:8000/api/v1/contacts \
      -H "Content-Type: application/json" \
      -d '{"lead_phone": "'$phone'", "source_id": 2, "message": "Тест"}' \
      | jq -r '.operator_id'
done | sort | uniq -c

echo ""
echo "Проверяем нагрузку операторов:"
curl -s http://localhost:8000/api/v1/operators | jq '.[] | select(.id == 3 or .id == 4) | {id, name, current_load, max_load}'
