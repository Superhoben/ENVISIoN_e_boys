/*********************************************************************************
 *
 * Inviwo - Interactive Visualization Workshop
 *
 * Copyright (c) 2017-2019 Inviwo Foundation
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice, this
 * list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 * this list of conditions and the following disclaimer in the documentation
 * and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
 * ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 *********************************************************************************/

#include <warn/push>
#include <warn/ignore/all>
#include <gtest/gtest.h>
#include <warn/pop>

#include <modules/fermi/fermimodule.h>

#include <inviwo/core/common/inviwoapplication.h>
#include <modules/python3/python3module.h>
#include <modules/python3/pythonscript.h>
#include <modules/python3/pybindutils.h>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <glm/gtc/epsilon.hpp>

namespace inviwo {

namespace {
std::string getPath() {
    auto path = util::getInviwoApplication()->getModuleByType<FermiModule>()->getPath(
        ModulePath::UnitTests);
    return path + "/scripts/";
}
}  // namespace

TEST(Python3Scripts, ExpandZone) {
    PythonScriptDisk script(getPath() + "expand_zone.py");

    bool status = false;
    script.run([&](pybind11::dict dict) {
        auto pyStatus = dict["status"];
        auto cStatus = pybind11::cast<bool>(pyStatus);

        EXPECT_TRUE(cStatus);
    });
}

TEST(Python3Scripts, BrillouinZone) {
    PythonScriptDisk script(getPath() + "brillouin_zone.py");

    bool status = false;
    script.run([&](pybind11::dict dict) {
        auto pyStatus = dict["status"];
        auto cStatus = pybind11::cast<bool>(pyStatus);

        EXPECT_TRUE(cStatus);
    });
}

} // namespace
