// 页面标题映射（App 侧边栏标题 + 浏览器 document.title 共用）

export const pageTitles = {
  home: '首页',
  teams: '组队广场',
  'team-detail': '队伍详情',
  notifications: '通知中心',
  profile: '个人中心'
}

export const defaultTitle = '竞赛组队系统'

export function titleFor(name) {
  return pageTitles[name] || defaultTitle
}
