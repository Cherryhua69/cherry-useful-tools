```javascript
function main(config) {
  const proxies = config.proxies || [];
  const jpNodes = proxies
    .map(p => p.name)
    .filter(name => /(JP|日本|🇯🇵)/i.test(name));

  if (jpNodes.length === 0) return config;

  config["proxy-groups"] = config["proxy-groups"] || [];
  config["proxy-groups"].unshift({
    name: "日本自动",
    type: "url-test",
    proxies: jpNodes,
    url: "https://cloudflare.com",
    interval: 300,
    tolerance: 50
  });

  // 可选：将首个 select 策略组加入“日本自动”选项
  const mainSelect = config["proxy-groups"].find(g => g.type === "select");
  if (mainSelect && Array.isArray(mainSelect.proxies) && !mainSelect.proxies.includes("日本自动")) {
    mainSelect.proxies.unshift("日本自动");
  }

  return config;
}
```
