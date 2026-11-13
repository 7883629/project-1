# Frontend

Vite + React + TypeScript。

## 已配置

- Tailwind CSS 4（`@tailwindcss/vite`）
- React Router
- Axios。开发环境把 `/api` 代理到 `http://127.0.0.1:8000`

## 启动

先启动后端：

```powershell
cd backend
uv run uvicorn main:app --reload --port 8000
```

再启动前端：

```powershell
cd frontend
npm run dev
```

浏览器打开 http://localhost:5173
