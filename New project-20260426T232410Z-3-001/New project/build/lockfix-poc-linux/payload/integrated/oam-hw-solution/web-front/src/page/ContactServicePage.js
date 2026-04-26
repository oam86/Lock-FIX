import React from 'react';


const ContactServicePage = props => {
    return (
        <div className="component-animation p-3 w-4/5 mx-auto bg-white rounded-lg shadow-md">
            {/* 상단 제목 */}
            <div className="bg-green-600 text-white text-center p-4 rounded-t-lg">
                <h1 className="text-2xl font-bold">우암전자 고객을 위한 원격지원 서비스</h1>
                <h2 className="text-lg mt-2">Remote support service for OAM Electronics Co., Ltd. of Customer</h2>
            </div>

            {/* 버튼 */}
            <div className="mt-6 text-center" style={{ marginBottom: '15px' }}>
                <a href="https://939.co.kr/as828282" target="_blank" rel="noopener noreferrer">
                    <button
                        className="bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-700 transition duration-200">
                        원격지원 접속 (Remote Support Access)
                    </button>
                </a>
            </div>

            {/* 이미지 */}
            <div className="flex justify-center mt-2"> {/* 이미지 가운데 정렬 */}
                <img src="/call.jpg" alt="Support Team" className="rounded-lg"
                     style={{height: '400px', width: '700px'}}/>
            </div>

            {/* 설명 텍스트 */}
            <div className="mt-4 text-center">
                <p className="text-sm text-gray-600">
                    기술 지원 안내 (Technical support information)
                    <br />
                    평일 09:00 ~ 18:00 (Weekdays 09:00 - 18:00)
                    <br />
                    고객 서비스 센터 (Customer Service Center): 1666-3776
                    <br />
                    Request Technical Service : tech@oooooam.com
                    <br />
                    Service Center : 070-7537-3438
                </p>
            </div>

            {/* 하단 정보 */}
            <div className="mt-8 text-center">
                <p className="text-sm text-gray-500">
                    OAM Electronics Co., Ltd.
                    <br />
                    서울특별시 송파구 충민로 66, 8층 8071호
                    <br />
                    8071F, 66, Chungmin-ro, Songpa-gu, Seoul, Republic of Korea
                    <br />
                    Tel : 1666-3736 Tech Support : 070-7537-3438 Zip code : 05854
                </p>
            </div>
        </div>
    );
};

export default ContactServicePage;