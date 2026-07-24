import axios from "axios";

export const apiClient = axios.create({
  baseURL: (import.meta as any).env.VITE_API_URL || "",
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

// Jamstack Interceptor: Reroute /api calls to local JSON files
apiClient.interceptors.request.use(async (config) => {
  const url = config.url || "";
  
  if (url.startsWith("/api/jobs") && config.method === "get") {
    // Return mock response wrapping jobs.json
    const res = await fetch("/data/jobs.json");
    const jobs = await res.json();
    
    // Check if it's a single job request e.g., /api/jobs/123
    const match = url.match(/\/api\/jobs\/(.+)/);
    if (match) {
      const jobId = match[1];
      const job = jobs.find((j: any) => j._id === jobId);
      config.adapter = async () => ({
        data: job,
        status: 200,
        statusText: "OK",
        headers: {},
        config,
      });
      return config;
    }
    
    // Otherwise return list of jobs
    config.adapter = async () => ({
      data: {
        jobs,
        total: jobs.length,
        page: 1,
        pages: 1
      },
      status: 200,
      statusText: "OK",
      headers: {},
      config,
    });
    return config;
  }
  
  if (url.startsWith("/api/insights") && config.method === "get") {
    const res = await fetch("/data/insights.json");
    const insights = await res.json();
    
    let responseData = {};
    if (url.includes("/dashboard")) responseData = insights.dashboard;
    else if (url.includes("/skill-graph")) responseData = insights.skill_graph;
    else if (url.includes("/salary-intelligence")) responseData = insights.salary_intelligence;
    else if (url.includes("/skill-clustering")) responseData = insights.clustering;
    else if (url.includes("/company-hiring-patterns")) responseData = insights.company_patterns;
    else if (url.includes("/company-skill-matrix")) responseData = insights.company_skills;
    else if (url.includes("/category-hiring-trends")) responseData = insights.category_trends;
    
    config.adapter = async () => ({
      data: responseData,
      status: 200,
      statusText: "OK",
      headers: {},
      config,
    });
    return config;
  }
  
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || "An error occurred";
    console.error("[API Error]", message);
    return Promise.reject(error);
  }
);
