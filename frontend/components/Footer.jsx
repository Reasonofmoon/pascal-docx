import { Heart, Github, Mail } from 'lucide-react'

const Footer = () => {
  return (
    <footer className="bg-gray-900 text-white mt-16">
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* 회사 정보 */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Pascal Education</h3>
            <p className="text-gray-300 text-sm leading-relaxed">
              AI 기반 영어 토론 교육 시스템으로 학습자의 비판적 사고력과 
              영어 실력을 동시에 향상시킵니다.
            </p>
          </div>

          {/* 빠른 링크 */}
          <div>
            <h3 className="text-lg font-semibold mb-4">빠른 링크</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <a href="/" className="text-gray-300 hover:text-white transition-colors">
                  홈
                </a>
              </li>
              <li>
                <a href="/analyze" className="text-gray-300 hover:text-white transition-colors">
                  원서 분석
                </a>
              </li>
              <li>
                <a href="/generate" className="text-gray-300 hover:text-white transition-colors">
                  교재 생성
                </a>
              </li>
            </ul>
          </div>

          {/* 연락처 */}
          <div>
            <h3 className="text-lg font-semibold mb-4">연락처</h3>
            <div className="space-y-2 text-sm">
              <div className="flex items-center space-x-2">
                <Mail className="h-4 w-4" />
                <span className="text-gray-300">contact@pascal-edu.com</span>
              </div>
              <div className="flex items-center space-x-2">
                <Github className="h-4 w-4" />
                <a 
                  href="https://github.com/pascal-edu" 
                  className="text-gray-300 hover:text-white transition-colors"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  GitHub
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* 하단 구분선 및 저작권 */}
        <div className="border-t border-gray-700 mt-8 pt-6">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <p className="text-gray-400 text-sm">
              © 2024 Pascal Education. All rights reserved.
            </p>
            <div className="flex items-center space-x-1 text-gray-400 text-sm mt-2 md:mt-0">
              <span>Made with</span>
              <Heart className="h-4 w-4 text-red-500" />
              <span>for education</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}

export default Footer
