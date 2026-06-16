# Схемы для диплома и презентации

Сгенерированные PNG/PDF — в этой же папке. Пересборка:

```powershell
python generate_diagrams.py
```

## Файлы

| Файл | Содержание |
|------|------------|
| `01_scene_tlas_blas` | Сцена testGI → BVH → TLAS → K BLAS на дом, rtsm::do_trace |
| `02_baseline_vs_optimized` | Baseline (перекрывающиеся AABB) vs MERGE-ALL (кластеры) |
| `03_merge_all_pipeline` | 6 шагов алгоритма MERGE-ALL |
| `04_testgi_scene_layout` | Сетка 4×4, камера, солнце |
| `05_k_sweep_chart` | График K_req → мс (данные из `data/Замеры/diff_K.md`) |
| `06_software_stack` | Стек: DX12 → bvh → testGI → rtsm |

## Вставка в LaTeX (диплом)

В преамбуле уже есть `\graphicspath{{images/}{images2/}}`. Пример:

```latex
\begin{figure}[h!]
\centering
\includegraphics[width=0.95\textwidth]{diagrams/01_scene_tlas_blas.pdf}
\caption{Архитектура ray tracing в testGI: TLAS агрегирует инстансы BLAS.}
\label{fig:tlas_blas}
\end{figure}
```

Для PNG замените расширение на `.png`.

## Презентация

Используйте `.png` (1920×… при масштабе figure) или `.pdf` для Beamer:

```latex
\includegraphics[width=\textwidth]{images/diagrams/05_k_sweep_chart.pdf}
```
