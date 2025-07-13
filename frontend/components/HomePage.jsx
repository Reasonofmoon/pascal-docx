import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  BookOpen, 
  FileText, 
  Sparkles, 
  Users, 
  Target, 
  Zap,
  ArrowRight,
  CheckCircle,
  Star
} from 'lucide-react'

const HomePage = () => {
  const features = [
    {
      icon: BookOpen,
      title: "AI 원서 분석",
      description: "영어 원서를 입력하면 AI가 자동으로 분석하여 토론 주제를 생성합니다.",
      color: "bg-blue-500"
    },
    {
      icon: FileText,
      title: "교재 자동 생성",
      description: "분석 결과를 바탕으로 완전한 출판 수준의 DOCX 교재를 생성합니다.",
      color: "bg-green-500"
    },
    {
      icon: Users,
      title: "레벨별 맞춤화",
      description: "기초, 발전, 숙달 단계별로 맞춤화된 토론 주제와 활동을 제공합니다.",
      color: "bg-purple-500"
    },
    {
      icon: Target,
      title: "체계적 학습",
      description: "독해, 어휘, 토론, 글쓰기가 통합된 체계적인 학습 경험을 제공합니다.",
      color: "bg-orange-500"
    }
  ]

  const benefits = [
    "AI 기반 자동 토론 주제 생성",
    "출판 수준의 완성도 높은 교재",
    "레벨별 맞춤형 학습 콘텐츠",
    "독해-토론-글쓰기 통합 학습",
    "한국 학습자 특화 설계",
    "즉시 사용 가능한 교육 자료"
  ]

  const stats = [
    { number: "1000+", label: "분석된 원서" },
    { number: "5000+", label: "생성된 토론 주제" },
    { number: "500+", label: "제작된 교재" },
    { number: "98%", label: "사용자 만족도" }
  ]

  return (
    <div className="space-y-16">
      {/* 히어로 섹션 */}
      <section className="text-center space-y-8">
        <div className="space-y-4">
          <Badge variant="secondary" className="px-4 py-2 text-sm">
            <Sparkles className="h-4 w-4 mr-2" />
            AI 기반 교육 솔루션
          </Badge>
          
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 leading-tight">
            영어 원서로 만드는
            <br />
            <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              AI 토론 교재
            </span>
          </h1>
          
          <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            원서 정보만 입력하면 AI가 자동으로 분석하여 체계적인 토론 주제와 
            완전한 교육 자료를 생성합니다. 출판 수준의 DOCX 교재를 즉시 제작하세요.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link to="/analyze">
            <Button size="lg" className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3">
              <BookOpen className="h-5 w-5 mr-2" />
              원서 분석 시작하기
              <ArrowRight className="h-5 w-5 ml-2" />
            </Button>
          </Link>
          
          <Link to="/generate">
            <Button size="lg" variant="outline" className="px-8 py-3">
              <FileText className="h-5 w-5 mr-2" />
              교재 생성하기
            </Button>
          </Link>
        </div>
      </section>

      {/* 통계 섹션 */}
      <section className="bg-white rounded-2xl shadow-lg p-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          {stats.map((stat, index) => (
            <div key={index} className="text-center">
              <div className="text-3xl md:text-4xl font-bold text-blue-600 mb-2">
                {stat.number}
              </div>
              <div className="text-gray-600 text-sm md:text-base">
                {stat.label}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* 주요 기능 섹션 */}
      <section className="space-y-8">
        <div className="text-center space-y-4">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900">
            주요 기능
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Pascal 시스템의 강력한 AI 기능으로 교육 자료 제작을 혁신하세요
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {features.map((feature, index) => {
            const Icon = feature.icon
            return (
              <Card key={index} className="hover:shadow-lg transition-shadow duration-300">
                <CardHeader>
                  <div className="flex items-center space-x-3">
                    <div className={`${feature.color} p-3 rounded-lg`}>
                      <Icon className="h-6 w-6 text-white" />
                    </div>
                    <CardTitle className="text-xl">{feature.title}</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base leading-relaxed">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            )
          })}
        </div>
      </section>

      {/* 혜택 섹션 */}
      <section className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
          <div className="space-y-6">
            <h2 className="text-3xl font-bold text-gray-900">
              왜 Pascal을 선택해야 할까요?
            </h2>
            <p className="text-lg text-gray-600 leading-relaxed">
              전통적인 교재 제작 방식을 혁신하여 시간과 비용을 대폭 절약하면서도 
              더 높은 품질의 교육 자료를 제공합니다.
            </p>
            <div className="space-y-3">
              {benefits.map((benefit, index) => (
                <div key={index} className="flex items-center space-x-3">
                  <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0" />
                  <span className="text-gray-700">{benefit}</span>
                </div>
              ))}
            </div>
          </div>
          
          <div className="relative">
            <div className="bg-white rounded-xl shadow-lg p-6 space-y-4">
              <div className="flex items-center space-x-2">
                <Star className="h-5 w-5 text-yellow-500" />
                <span className="font-semibold">사용자 후기</span>
              </div>
              <blockquote className="text-gray-600 italic">
                "Pascal 덕분에 교재 제작 시간이 90% 단축되었습니다. 
                AI가 생성한 토론 주제의 품질도 매우 우수해요!"
              </blockquote>
              <div className="text-sm text-gray-500">
                - 김선생님, 영어교육 전문가
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA 섹션 */}
      <section className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl p-8 text-center text-white">
        <div className="space-y-6">
          <h2 className="text-3xl md:text-4xl font-bold">
            지금 바로 시작해보세요
          </h2>
          <p className="text-xl opacity-90 max-w-2xl mx-auto">
            몇 분 안에 완전한 토론 교재를 만들어보세요. 
            복잡한 설정이나 학습 과정이 필요하지 않습니다.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/analyze">
              <Button size="lg" variant="secondary" className="px-8 py-3">
                <Zap className="h-5 w-5 mr-2" />
                무료로 시작하기
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  )
}

export default HomePage
